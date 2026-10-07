//! Measures how frame time in Bevy moves with triangles per asset, texture size and the number
//! of assets on screen, for the pit target profile's budgets.
//!
//! Usage: budget_bench --out <dir> [--repeats N] [--only <name prefix>] [--windowed]
//!
//! Scenes are run in groups: one process with one full-screen window draws a group's scenes in
//! turn. Every repeat runs every group. Before the repeats, a few scenes are run in a process
//! each to read their video memory. Writes into `<dir>`:
//!
//! - `results.csv`: one row per scene per repeat.
//! - `summary.csv`: one row per scene, the middle repeat and the spread across repeats.
//! - `memory.csv`: video memory of the scenes run alone.
//! - `environment.json`: versions, hardware, settings and what else was on the GPU.

// The `json!` object that holds one scene's result is long.
#![recursion_limit = "256"]

mod case;
mod run;
mod scene;

use std::{
    collections::BTreeMap,
    path::{Path, PathBuf},
    process::Command,
    time::{Duration, Instant},
};

use bevy::app::AppExit;
use serde_json::{Value, json};

use case::Case;

const USAGE: &str = "usage: budget_bench --out <dir> [--repeats N] [--only <name prefix>] [--windowed]";

/// The result fields that become columns of `results.csv`, in order.
const COLUMNS: &[&str] = &[
    "name",
    "repeat",
    "count",
    "tris_per_asset",
    "texture_size",
    "unique_assets",
    "shadows",
    "mips",
    "format",
    "msaa",
    "lod",
    "cascades",
    "triangles_total",
    "vertices_total",
    "meshes",
    "textures",
    "texture_mib_computed",
    "mesh_mib_computed",
    "farthest_asset_m",
    "window_width",
    "window_height",
    "frames",
    "frame_ms_median",
    "frame_ms_mean",
    "frame_ms_p95",
    "frame_ms_p99",
    "frame_ms_min",
    "frame_ms_max",
    "drift_percent",
    "gpu_pass_ms",
    "opaque_pass_gpu_ms",
    "opaque_triangles_drawn",
    "opaque_fragments",
    "gpu_utilisation_percent",
];
/// The columns that describe the scene and are the same in every repeat.
const SCENE_COLUMNS: std::ops::Range<usize> = 2..13;
/// The measured columns `summary.csv` gives the middle repeat of.
const SUMMARY_COLUMNS: &[&str] =
    &["frame_ms_p95", "frame_ms_p99", "gpu_pass_ms", "opaque_pass_gpu_ms", "opaque_triangles_drawn", "gpu_utilisation_percent"];
const MEMORY_COLUMNS: &[&str] = &[
    "name",
    "count",
    "unique_assets",
    "tris_per_asset",
    "texture_size",
    "mips",
    "format",
    "texture_mib_computed",
    "mesh_mib_computed",
    "vram_before_mib",
    "vram_used_mib",
    "vram_delta_mib",
    "vram_process_mib",
];

fn main() -> AppExit {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let value_of = |flag: &str| args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned();
    let has = |flag: &str| args.iter().any(|a| a == flag);

    // The form the driver below starts: every scene of a group as its own --case.
    if let Some(result) = value_of("--result") {
        let cases: Result<Vec<Case>, String> =
            args.windows(2).filter(|pair| pair[0] == "--case").map(|pair| Case::from_arg(&pair[1])).collect();
        return match cases {
            Ok(cases) => run::run(cases, PathBuf::from(result), has("--windowed"), has("--quick")),
            Err(error) => {
                eprintln!("bad --case: {error}");
                AppExit::error()
            }
        };
    }

    let Some(out) = value_of("--out").map(PathBuf::from) else {
        eprintln!("{USAGE}");
        return AppExit::error();
    };
    let repeats: u32 = value_of("--repeats").and_then(|n| n.parse().ok()).unwrap_or(3);
    let only = value_of("--only").unwrap_or_default();
    match drive(&out, repeats, &only, has("--windowed")) {
        Ok(()) => AppExit::Success,
        Err(error) => {
            eprintln!("budget_bench: {error}");
            AppExit::error()
        }
    }
}

/// Starts one process that draws `cases` in turn, and returns one result per scene.
fn run_scenes(cases: &[Case], scratch: &Path, extra: &[&str]) -> Result<Vec<Value>, String> {
    let exe = std::env::current_exe().map_err(|e| e.to_string())?;
    let _ = std::fs::remove_file(scratch);
    let mut command = Command::new(&exe);
    command.arg("--result").arg(scratch).args(extra);
    for case in cases {
        command.args(["--case", &case.to_arg()]);
    }
    let status = command.status().map_err(|e| format!("cannot start {}: {e}", exe.display()))?;
    let text = std::fs::read_to_string(scratch).unwrap_or_default();
    let _ = std::fs::remove_file(scratch);
    let results: Vec<Value> = text.lines().map(serde_json::from_str).collect::<Result<_, _>>().map_err(|e| e.to_string())?;
    if !status.success() || results.len() != cases.len() {
        return Err(format!("stopped after {} of {} scenes, at {} ({status})", results.len(), cases.len(), cases[results.len()].name));
    }
    Ok(results)
}

fn drive(out: &Path, repeats: u32, only: &str, windowed: bool) -> Result<(), String> {
    let began = Instant::now();
    std::fs::create_dir_all(out).map_err(|e| format!("cannot create {}: {e}", out.display()))?;
    // Each group's scenes, then the check scene that shows whether they slowed later frames.
    let groups: Vec<(&str, Vec<Case>)> = case::groups()
        .into_iter()
        .map(|group| (group.name, group.cases.into_iter().filter(|case| case.name.starts_with(only)).collect::<Vec<_>>()))
        .filter(|(_, cases)| !cases.is_empty())
        .map(|(name, mut cases)| {
            cases.push(case::check_case(name));
            (name, cases)
        })
        .collect();
    if groups.is_empty() {
        return Err(format!("no scene's name starts with {only:?}"));
    }
    let scratch = out.join("results.jsonl");
    let extra: &[&str] = if windowed { &["--windowed"] } else { &[] };
    let gpu_before = command_text("nvidia-smi", &[]);

    println!("video memory, one process per scene");
    let mut memory = Vec::new();
    for case in case::memory_cases().into_iter().filter(|case| case.name.starts_with(only)) {
        // Give the last process's memory time to be handed back.
        std::thread::sleep(Duration::from_secs(1));
        let before = nvidia_now().0;
        let mut result = run_scenes(std::slice::from_ref(&case), &scratch, &[extra, &["--quick"]].concat())?.remove(0);
        result["vram_before_mib"] = json!(before);
        result["vram_delta_mib"] = json!(result["vram_used_mib"].as_f64().zip(before).map(|(used, before)| used - before));
        memory.push(result);
    }

    // Every repeat runs every scene, so anything that drifts during the measurement
    // (temperature, other programs) is spread across the scenes instead of landing on a few.
    let mut results: Vec<Value> = Vec::new();
    for repeat in 1..=repeats {
        for (name, cases) in &groups {
            println!("repeat {repeat} of {repeats}, group {name}");
            for mut result in run_scenes(cases, &scratch, extra)? {
                result["repeat"] = json!(repeat);
                results.push(result);
            }
        }
    }

    let write = |name: &str, text: String| std::fs::write(out.join(name), text).map_err(|e| format!("cannot write {name}: {e}"));
    write("results.csv", csv(COLUMNS, &results))?;
    write("summary.csv", summary_csv(&results))?;
    write("memory.csv", csv(MEMORY_COLUMNS, &memory))?;
    let seconds = began.elapsed().as_secs_f64();
    let environment = json!({
        "bevy": locked_version("bevy"),
        "wgpu": locked_version("wgpu"),
        "commit": command_text("git", &["rev-parse", "HEAD"]).trim(),
        "uncommitted_changes": !command_text("git", &["status", "--porcelain", "--untracked-files=no"]).trim().is_empty(),
        "build": if cfg!(debug_assertions) { "debug" } else { "release" },
        "adapter": results[0]["adapter"], "backend": results[0]["backend"], "driver": results[0]["driver"],
        "cpu": cpu_model(),
        "kernel": command_text("uname", &["-sr"]).trim(),
        "desktop": std::env::var("XDG_CURRENT_DESKTOP").unwrap_or_default(),
        "session": std::env::var("XDG_SESSION_TYPE").unwrap_or_default(),
        "repeats": repeats, "scenes_per_repeat": results.len() / repeats.max(1) as usize,
        "wall_clock_seconds": seconds.round(),
        "settings": run::settings(),
        "render_diagnostics_of_last_scene": results[results.len() - 1]["render_diagnostics"],
        "nvidia_smi_before": gpu_before.lines().collect::<Vec<_>>(),
        "nvidia_smi_after": command_text("nvidia-smi", &[]).lines().collect::<Vec<_>>(),
    });
    write("environment.json", serde_json::to_string_pretty(&environment).unwrap() + "\n")?;
    println!("{} scenes x {repeats} repeats in {seconds:.0} s; results in {}", results.len() / repeats.max(1) as usize, out.display());
    Ok(())
}

fn cell(value: &Value) -> String {
    match value {
        Value::Null => String::new(),
        Value::String(s) => s.clone(),
        Value::Bool(b) => (*b as u8).to_string(),
        Value::Number(n) if n.is_f64() => number(n.as_f64().unwrap()),
        other => other.to_string(),
    }
}

/// Four decimal places, without trailing zeros.
fn number(value: f64) -> String {
    if !value.is_finite() {
        return String::new();
    }
    let text = format!("{value:.4}");
    text.trim_end_matches('0').trim_end_matches('.').to_string()
}

fn csv(columns: &[&str], results: &[Value]) -> String {
    let mut text = columns.join(",") + "\n";
    for result in results {
        let row: Vec<String> = columns.iter().map(|column| cell(&result[*column])).collect();
        text += &(row.join(",") + "\n");
    }
    text
}

/// One row per scene: the middle repeat of each figure, and the spread of the median frame time
/// across repeats, which is the noise any comparison has to clear.
fn summary_csv(results: &[Value]) -> String {
    let mut names: Vec<&str> = Vec::new();
    let mut by_name: BTreeMap<&str, Vec<&Value>> = BTreeMap::new();
    for result in results {
        let name = result["name"].as_str().unwrap();
        if !by_name.contains_key(name) {
            names.push(name);
        }
        by_name.entry(name).or_default().push(result);
    }
    let mut header = vec!["name"];
    header.extend(&COLUMNS[SCENE_COLUMNS]);
    header.extend(["farthest_asset_m", "frame_ms_median", "frame_ms_median_lowest", "frame_ms_median_highest", "spread_percent"]);
    header.extend(SUMMARY_COLUMNS);
    let mut text = header.join(",") + "\n";
    for name in names {
        let runs = &by_name[name];
        let middle = |column: &str| {
            let mut values: Vec<f64> = runs.iter().filter_map(|run| run[column].as_f64()).collect();
            values.sort_by(f64::total_cmp);
            if values.is_empty() { f64::NAN } else { values[(values.len() - 1) / 2] }
        };
        let medians: Vec<f64> = runs.iter().filter_map(|run| run["frame_ms_median"].as_f64()).collect();
        let lowest = medians.iter().copied().fold(f64::INFINITY, f64::min);
        let highest = medians.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        let median = middle("frame_ms_median");
        let mut row = vec![name.to_string()];
        row.extend(COLUMNS[SCENE_COLUMNS].iter().map(|column| cell(&runs[0][*column])));
        row.push(cell(&runs[0]["farthest_asset_m"]));
        row.extend([median, lowest, highest, (highest - lowest) / median * 100.0].map(number));
        row.extend(SUMMARY_COLUMNS.iter().map(|column| number(middle(column))));
        text += &(row.join(",") + "\n");
    }
    text
}

/// Video memory in use on the whole GPU, in MiB, and how busy the GPU was over the driver's
/// last sample period, in percent. `None` where `nvidia-smi` is missing.
pub fn nvidia_now() -> (Option<f64>, Option<f64>) {
    let text = command_text("nvidia-smi", &["--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"]);
    let mut numbers = text.lines().next().unwrap_or_default().split(',').map(|n| n.trim().parse::<f64>().ok());
    (numbers.next().flatten(), numbers.next().flatten())
}

/// Video memory the driver counts against one process, in MiB, read from the process table
/// `nvidia-smi` prints. Unlike the whole-GPU figure it does not move when the desktop's own
/// use does.
pub fn nvidia_process_mib(pid: u32) -> Option<f64> {
    let pid = pid.to_string();
    command_text("nvidia-smi", &[]).lines().find_map(|line| {
        // A row reads: | GPU GI CI PID Type Name Memory |
        let fields: Vec<&str> = line.split_whitespace().collect();
        (fields.get(4) == Some(&pid.as_str())).then(|| fields.iter().rev().find_map(|field| field.strip_suffix("MiB")?.parse().ok())).flatten()
    })
}

fn command_text(program: &str, args: &[&str]) -> String {
    Command::new(program).args(args).output().map(|o| String::from_utf8_lossy(&o.stdout).into_owned()).unwrap_or_default()
}

/// The version of a crate in this workspace's lock file, as it was when this was built.
fn locked_version(name: &str) -> String {
    let lock = include_str!("../../../Cargo.lock");
    let mut lines = lock.lines();
    while let Some(line) = lines.next() {
        if line == format!("name = \"{name}\"") {
            return lines.next().unwrap_or_default().trim_start_matches("version = ").trim_matches('"').to_string();
        }
    }
    String::new()
}

fn cpu_model() -> String {
    std::fs::read_to_string("/proc/cpuinfo")
        .unwrap_or_default()
        .lines()
        .find_map(|line| line.strip_prefix("model name").map(|rest| rest.trim_start_matches([' ', '\t', ':']).to_string()))
        .unwrap_or_default()
}
