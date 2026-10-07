//! One measured scene, and the list of scenes a full measurement runs.

use std::fmt::Write;

/// How texture pixels are stored on the GPU.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum TexFormat {
    /// Uncompressed, 4 bytes per pixel.
    Rgba8,
    /// Block compressed, 1 byte per pixel. The blocks are random bytes: the cost of storing and
    /// sampling them does not depend on what they show.
    Bc7,
}

/// One scene: a number of assets in front of a first-person camera.
#[derive(Clone, Debug)]
pub struct Case {
    pub name: String,
    /// Assets on screen.
    pub count: u32,
    /// Triangles in each asset at full detail.
    pub tris: u32,
    /// Width and height in pixels of each of an asset's three textures.
    pub tex: u32,
    /// How many different assets (own mesh, own material, own three textures) the `count`
    /// instances are drawn from. 0 means every instance is different.
    pub unique: u32,
    pub shadows: bool,
    pub mips: bool,
    pub format: TexFormat,
    /// Samples per pixel for multisample anti-aliasing: 1 (off) or 4 (Bevy's default).
    pub msaa: u32,
    /// Whether far assets use meshes with fewer triangles (levels of detail).
    pub lod: bool,
    /// Shadow cascades: how many shadow maps the sun draws, each covering a band of distance.
    /// Bevy's default is 4.
    pub cascades: u32,
}

impl Case {
    /// The middle of every sweep: the values held while one variable moves.
    pub fn middle(name: &str) -> Self {
        Self {
            name: name.into(),
            count: 100,
            tris: 10_000,
            tex: 1024,
            unique: 0,
            shadows: true,
            mips: true,
            format: TexFormat::Rgba8,
            msaa: 4,
            lod: false,
            cascades: 4,
        }
    }

    /// Number of different assets in the scene.
    pub fn unique_assets(&self) -> u32 {
        if self.unique == 0 { self.count } else { self.unique.min(self.count) }
    }

    pub fn to_arg(&self) -> String {
        let mut s = String::new();
        write!(
            s,
            "name={},count={},tris={},tex={},unique={},shadows={},mips={},format={},msaa={},lod={},cascades={}",
            self.name,
            self.count,
            self.tris,
            self.tex,
            self.unique,
            self.shadows as u8,
            self.mips as u8,
            match self.format {
                TexFormat::Rgba8 => "rgba8",
                TexFormat::Bc7 => "bc7",
            },
            self.msaa,
            self.lod as u8,
            self.cascades,
        )
        .unwrap();
        s
    }

    pub fn from_arg(arg: &str) -> Result<Self, String> {
        let mut case = Self::middle("");
        for pair in arg.split(',') {
            let (key, value) = pair.split_once('=').ok_or_else(|| format!("not key=value: {pair}"))?;
            let number = || value.parse::<u32>().map_err(|e| format!("{key}: {e}"));
            match key {
                "name" => case.name = value.to_string(),
                "count" => case.count = number()?,
                "tris" => case.tris = number()?,
                "tex" => case.tex = number()?,
                "unique" => case.unique = number()?,
                "shadows" => case.shadows = number()? != 0,
                "mips" => case.mips = number()? != 0,
                "msaa" => case.msaa = number()?,
                "lod" => case.lod = number()? != 0,
                "cascades" => case.cascades = number()?,
                "format" => {
                    case.format = match value {
                        "rgba8" => TexFormat::Rgba8,
                        "bc7" => TexFormat::Bc7,
                        other => return Err(format!("unknown format {other}")),
                    }
                }
                other => return Err(format!("unknown key {other}")),
            }
        }
        Ok(case)
    }
}

fn short(n: u32) -> String {
    if n >= 1_000_000 && n.is_multiple_of(1_000_000) {
        format!("{}m", n / 1_000_000)
    } else if n >= 1000 && n.is_multiple_of(1000) {
        format!("{}k", n / 1000)
    } else {
        n.to_string()
    }
}

/// Scenes that are drawn one after another by one process, in one window.
pub struct Group {
    pub name: &'static str,
    pub cases: Vec<Case>,
}

/// The scene drawn again at the end of every group, named `check-<group>`. Its frame time is
/// short and limited by the CPU, so it shows whether the scenes before it left anything behind
/// that slows later frames: compare it with `tris-10k`, the same scene early in a process.
pub fn check_case(group: &str) -> Case {
    Case::middle(&format!("check-{group}"))
}

/// Every scene of the full measurement, in the order it is run.
///
/// A new process starts for each group because Bevy keeps some per-frame work sized to the
/// largest scene it has drawn; scenes with thousands of different assets come last.
pub fn groups() -> Vec<Group> {
    let mid = Case::middle;

    // Nothing but the ground and the light: the fixed cost of a frame.
    let mut triangles = vec![Case { count: 0, ..mid("empty") }, Case { count: 0, shadows: false, ..mid("empty-noshadow") }];
    // 1. Triangles per asset, 100 different assets.
    for tris in [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000] {
        triangles.push(Case { tris, ..mid(&format!("tris-{}", short(tris))) });
    }
    for tris in [1_000, 10_000, 50_000, 100_000, 500_000, 1_000_000] {
        triangles.push(Case { tris, shadows: false, ..mid(&format!("tris-noshadow-{}", short(tris))) });
    }

    // 2. Texture size: 300 assets drawn from 12 different ones, so that 4096 fits in memory.
    let mut textures = Vec::new();
    let tex = |name: String| Case { count: 300, unique: 12, ..mid(&name) };
    for size in [256, 512, 1024, 2048, 4096] {
        textures.push(Case { tex: size, ..tex(format!("tex-{size}")) });
    }
    for size in [1024, 4096] {
        textures.push(Case { tex: size, mips: false, ..tex(format!("tex-nomips-{size}")) });
    }
    for size in [1024, 2048, 4096] {
        textures.push(Case { tex: size, format: TexFormat::Bc7, ..tex(format!("tex-bc7-{size}")) });
    }

    // 3. Assets on screen, drawn from 64 different assets (the realistic case).
    let mut counts = Vec::new();
    for count in [1, 10, 30, 100, 300, 1000, 3000] {
        counts.push(Case { count, unique: 64, ..mid(&format!("count-{}", short(count))) });
    }
    for count in [100, 1000, 3000] {
        counts.push(Case { count, unique: 64, shadows: false, ..mid(&format!("count-noshadow-{}", short(count))) });
    }
    // The same with one asset repeated, the best case for the engine's batching.
    for count in [100, 1000, 3000] {
        counts.push(Case { count, unique: 1, ..mid(&format!("count-shared-{}", short(count))) });
    }

    // Combined points near the expected budget.
    let points = [(300, 20_000), (300, 50_000), (1000, 20_000), (1000, 50_000), (3000, 20_000)];
    let mut mixes = Vec::new();
    for (count, tris) in points {
        mixes.push(Case { count, tris, unique: 64, ..mid(&format!("mix-{}x{}", short(count), short(tris))) });
    }
    // Fewer shadow cascades, to show how much of the shadow cost is the number of shadow maps.
    for cascades in [1, 2] {
        mixes.push(Case { count: 1000, tris: 20_000, unique: 64, cascades, ..mid(&format!("cascades-{cascades}-1kx20k")) });
    }
    // Anti-aliasing off, to show how much of a frame is per-pixel work.
    mixes.push(Case { msaa: 1, ..mid("msaa-off-100x10k") });
    mixes.push(Case { count: 1000, tris: 20_000, unique: 64, msaa: 1, ..mid("msaa-off-1kx20k") });

    // The same points and counts with levels of detail.
    let mut lods = Vec::new();
    for count in [1000, 3000] {
        lods.push(Case { count, unique: 64, lod: true, ..mid(&format!("count-{}-lod", short(count))) });
    }
    for (count, tris) in points {
        lods.push(Case { count, tris, unique: 64, lod: true, ..mid(&format!("mix-{}x{}-lod", short(count), short(tris))) });
    }

    // Assets on screen with every asset different (small textures so 3000 sets fit in memory).
    let mut distinct = Vec::new();
    for count in [100, 1000, 3000] {
        distinct.push(Case { count, tex: 256, ..mid(&format!("count-distinct-{}", short(count))) });
    }

    vec![
        Group { name: "triangles", cases: triangles },
        Group { name: "textures", cases: textures },
        Group { name: "counts", cases: counts },
        Group { name: "mixes", cases: mixes },
        Group { name: "lods", cases: lods },
        Group { name: "distinct", cases: distinct },
    ]
}

/// Scenes whose video memory is measured, each in a process of its own: a process does not
/// hand memory back between scenes, so memory read inside a group says nothing.
pub fn memory_cases() -> Vec<Case> {
    let wanted = ["empty", "tex-1024", "tex-2048", "tex-4096", "tex-bc7-2048", "tex-bc7-4096", "tris-10k", "tris-1m"];
    let all: Vec<Case> = groups().into_iter().flat_map(|group| group.cases).collect();
    wanted.iter().map(|name| all.iter().find(|case| case.name == *name).expect("a memory scene is in no group").clone()).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_case_survives_the_trip_through_its_argument() {
        for case in groups().into_iter().flat_map(|group| group.cases) {
            assert_eq!(Case::from_arg(&case.to_arg()).unwrap().to_arg(), case.to_arg());
        }
    }

    #[test]
    fn scene_names_are_unique() {
        let mut names: Vec<String> = groups().into_iter().flat_map(|group| group.cases).map(|case| case.name).collect();
        let count = names.len();
        names.sort();
        names.dedup();
        assert_eq!(names.len(), count);
        assert_eq!(memory_cases().len(), 8);
    }
}
