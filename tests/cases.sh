# The cases of tests/run.sh: every check must be able to fail.
#
# One case per line, and nothing else but comments and `uses` lines. A case is
#   expect <exit code> "<name>" <command...>      the command must exit with that code
#   expect_id "<check id>" "<name>" <command...>  the command must exit 1 and name that check
# Its name starts with its gate (L0, L1, L2b, L2c, L4, L4b, L4c, L4d, L5b, L5c) and is unique.
# `uses <tag...>` says what the cases below it depend on, until the next `uses`: the assets they
# read, and the tools behind them (see `tags_of_file` in tests/run.sh). Selection goes by these.
#
# tests/run.sh runs each line in a shell of its own, in any order and several at once, so a case
# may not depend on another: it writes only under its own "$tmp", and anything two cases share
# is a fixture (`broken`, `broken_tree`, `broken_slab`, `broken_pebble`, `exported`, `flipped_normals`, `bark_shot`, `once`), built once by whichever
# case asks first. The helpers are in tests/run.sh.

# The build's bake, when it is done on the graphics card (KILN_BAKE=gpu): a card out of memory leaves a wrong
# texture and reports the bake finished, so tools/paint.py compares it with a small bake on the CPU. Filed under L1, the first gate after the build.
uses paint bake_check
expect 0 "L1 bake check passes a right bake on the graphics card"                              tools/bl tests/bake_check.py right
expect_id "bake.agrees_with_cpu" "L1 bake check catches a bake that left the texture black"    tools/bl tests/bake_check.py black
expect_id "bake.agrees_with_cpu" "L1 bake check catches a bake wrong in a fifth of the texture" tools/bl tests/bake_check.py part_wrong
expect_id "bake.agrees_with_cpu" "L1 bake check catches a bake that missed one island"         tools/bl tests/bake_check.py island_missing

# L1: each asset broken one way at a time inside Blender (tests/test_validate.py lists the mutations).
uses tracer validate
expect 0 "L1 mutation tests: tracer" l1 tracer
uses crate validate
expect 0 "L1 mutation tests: crate" l1 crate
uses rock validate paint
expect 0 "L1 mutation tests: rock" l1 rock
# tree_1's are done in shares side by side, and its unbroken check, which builds its two siblings, apart.
uses tree_1 tree_2 tree_3 validate paint
expect 0 "L1 mutation tests: tree_1, unbroken" l1 tree_1 --unbroken
uses tree_1 validate paint
expect 0 "L1 mutation tests: tree_1, part 1 of 6" l1 tree_1 --part 1/6
expect 0 "L1 mutation tests: tree_1, part 2 of 6" l1 tree_1 --part 2/6
expect 0 "L1 mutation tests: tree_1, part 3 of 6" l1 tree_1 --part 3/6
expect 0 "L1 mutation tests: tree_1, part 4 of 6" l1 tree_1 --part 4/6
expect 0 "L1 mutation tests: tree_1, part 5 of 6" l1 tree_1 --part 5/6
expect 0 "L1 mutation tests: tree_1, part 6 of 6" l1 tree_1 --part 6/6
# A plant of blades (source/blade_plant): its blades broken one way at a time.
uses blade_plant_1 blade_plant_2 blade_plant_3 validate paint
expect 0 "L1 mutation tests: blade_plant_1" l1 blade_plant_1

uses slab_1 validate paint
expect 0 "L1 mutation tests: slab_1" l1 slab_1
# A pebble (source/pebble): made too tall for its width, and cut into a block with one big steep face.
uses pebble_2 validate paint
expect 0 "L1 mutation tests: pebble_2" l1 pebble_2
# A crag (source/crag): its prisms' heights and leans broken one way at a time.
uses crag_1 validate paint
expect 0 "L1 mutation tests: crag_1" l1 crag_1
# A block (source/block): its squareness, its chamfers and its crack broken one way at a time.
uses block_2 validate paint
expect 0 "L1 mutation tests: block_2" l1 block_2

# A table rock (source/table_rock): its cap and neck broken one way at a time.
uses table_rock_1 validate paint
expect 0 "L1 mutation tests: table_rock_1" l1 table_rock_1

uses tracer smoke
expect 0 "L4 passes the real manifest"      smoke "$glb" "$manifest"
expect 1 "L4 catches a triangle mismatch"   smoke "$glb" "$(tamper 'm["triangles"] += 1')"
expect 1 "L4 catches a missing node"        smoke "$glb" "$(tamper 'm["nodes"] = ["nope"]')"
expect 1 "L4 catches a missing attribute"   smoke "$glb" "$(tamper 'm["attributes"] += ["TANGENT"]')"
expect 1 "L4 catches reversed facing"       smoke "$glb" "$(tamper 'b=m["bounds"]; b["min"][2], b["max"][2] = -b["max"][2], -b["min"][2]')"
expect 1 "L4 catches a Z-up export"         smoke "$glb" "$(tamper 'b=m["bounds"]; b["min"] = [-0.5, -1.5, 0.0]; b["max"] = [1.0, 0.5, 1.0]')"
expect 1 "L4 catches a wrong scale"         smoke "$glb" "$(tamper 'b=m["bounds"]; b["max"] = [v * 100 for v in b["max"]]')"
expect 1 "L4 catches a wrong colour"         smoke "$glb" "$(tamper 'm["materials"]["m_tracer"][0] += 0.05')"
expect 1 "L4 catches a renamed material"    smoke "$glb" "$(tamper 'm["materials"] = {"m_other": [0.5, 0.5, 0.5]}')"
uses tracer smoke flip_normals
expect 1 "L4 catches normals against winding" smoke "$(flipped_normals)" "$manifest"
uses tracer smoke
expect 1 "L4 catches an inside-out mesh"    smoke "$(exported inside_out)" "$manifest"
# Overlapping pieces (ADR 13): the tracer with a small box pushed into its leg, and a manifest that says so.
expect 0 "L4 passes two closed pieces that overlap" smoke "$(exported two_pieces)" "$(tamper 'm["triangles"] += 12; m["overlap"] = True')"
expect_id "pieces.outward" "L4 catches one piece inside out among several" smoke "$(exported piece_inside_out)" "$(tamper 'm["triangles"] += 12; m["overlap"] = True')"
# The rock with every face lit flat: the same triangles, but no soft edges.
uses rock smoke
expect 0 "L4 passes the real rock"          smoke assets/models/rock.glb assets/models/rock.manifest.json
expect 1 "L4 catches hard edges on a soft-edged asset" smoke "$(exported hard_edges)" assets/models/rock.manifest.json

# Painted shading: the rock painted wrongly, or laid out wrongly, against the real manifest.
expect_id "flat.no_texture"        "L4 catches a texture on a flat-coloured asset"  smoke "$rock" "$(tamper 'del m["painted"]' "$rock_manifest")"
uses rock smoke paint rock_mutations
expect_id "painted.present"        "L4 catches a painted asset with no texture"     smoke "$(broken unpainted)" "$rock_manifest"
uses tracer rock smoke
expect_id "painted.present"        "L4 catches painted shading asked of a flat asset" smoke "$glb" "$(tamper 'm["painted"] = json.load(open("'$rock_manifest'"))["painted"]')"
uses rock smoke paint rock_mutations
expect_id "painted.factor"         "L4 catches a tint multiplied over the texture"  smoke "$(broken tinted_factor)" "$rock_manifest"
expect_id "painted.texture_size"   "L4 catches a texture of the wrong size"         smoke "$(broken small_texture)" "$rock_manifest"
expect_id "painted.colour"         "L4 catches paint over the wrong colour"         smoke "$(broken wrong_colour)" "$rock_manifest"
expect_id "painted.gradient"       "L4 catches a missing base-to-top gradient"      smoke "$(broken no_gradient)" "$rock_manifest"
expect_id "painted.edges_lighter"  "L4 catches missing edge light"                  smoke "$(broken no_edge_light)" "$rock_manifest"
expect_id "painted.crevices_darker" "L4 catches a missing crevice shadow"           smoke "$(broken no_crevice_shadow)" "$rock_manifest"
expect_id "painted.range"          "L4 catches texels burnt out to white"           smoke "$(broken burnt_out)" "$rock_manifest"
expect_id "painted.banding"        "L4 catches a gradient in visible steps"          smoke "$(broken banded)" "$rock_manifest"
expect_id "painted.growth_height"  "L4 catches a rock with no growth at its base"    smoke "$(broken no_growth)" "$rock_manifest"
expect_id "painted.growth_height"  "L4 catches growth all the way up the sides"      smoke "$(broken growth_everywhere)" "$rock_manifest"
expect_id "painted.growth_up"      "L4 catches bare upward-facing surfaces"          smoke "$(broken no_growth_up)" "$rock_manifest"
expect_id "painted.growth_up"      "L4 catches growth carpeting the top, not patchy" smoke "$(broken growth_carpets_the_top)" "$rock_manifest"
expect_id "painted.growth_edges"   "L4 catches bare upper edges"                     smoke "$(broken no_growth_edges)" "$rock_manifest"
expect_id "painted.growth_darker"  "L4 catches growth no darker than the rock"       smoke "$(broken growth_not_darker)" "$rock_manifest"
expect_id "painted.growth_patches" "L4 catches growth in broad patches"              smoke "$(broken growth_broad_patches)" "$rock_manifest"
expect_id "painted.blotches"       "L4 catches planes with no blotches"              smoke "$(broken no_blotches)" "$rock_manifest"
expect_id "painted.blotches"       "L4 catches blotches stronger than asked"         smoke "$(broken harsh_blotches)" "$rock_manifest"
expect_id "painted.blotches_broad" "L4 catches blotches as fine grain"               smoke "$(broken speckle)" "$rock_manifest"
expect_id "painted.side_shade"     "L4 catches sides not darker at mid height"       smoke "$(broken no_side_shade)" "$rock_manifest"
uses rock smoke
expect_id "painted.open_faces"     "L4 catches an edge width that leaves no open face" smoke "$rock" "$(tamper 'm["painted"]["edge_width_m"] = 5.0' "$rock_manifest")"
uses rock smoke paint rock_mutations
expect_id "uv.no_overlap"          "L4 catches overlapping UVs"                     smoke "$(broken stacked_uvs)" "$rock_manifest"
expect_id "uv.in_unit_square"      "L4 catches UVs off the texture"                 smoke "$(broken uvs_off_the_texture)" "$rock_manifest"
# One load of the rock with its UVs shrunk must fail both checks: `once` runs it for whichever case asks first.
expect_id "uv.coverage"            "L4 catches a mostly unused texture"             once shrunk smoke "$(broken shrunk_uvs)" "$rock_manifest"
expect_id "uv.texel_density"       "L4 catches texels too coarse for 0.5 m"         once shrunk smoke "$(broken shrunk_uvs)" "$rock_manifest"

# Foliage: tree_1 with its leaf pieces coloured, lit or exported wrongly, against the real manifest.
uses tree_1 smoke
expect 0 "L4 passes the real tree"          smoke "$tree" "$tree_manifest"
uses tree_1 smoke paint tree_mutations
expect 0 "L4 passes an unbroken tree from the mutation script" smoke "$(broken_tree none)" "$tree_manifest"
expect_id "foliage.two_sided"      "L4 catches leaves seen from one side only"      smoke "$(broken_tree single_sided)" "$tree_manifest"
expect_id "foliage.flat_colour"    "L4 catches a gradient within a leaf piece"      smoke "$(broken_tree gradient_within_piece)" "$tree_manifest"
expect_id "foliage.palette"        "L4 catches leaves painted from another colour"  smoke "$(broken_tree wrong_leaf_colour)" "$tree_manifest"
expect_id "foliage.colour_varies"  "L4 catches neighbouring leaves all one tone"    smoke "$(broken_tree one_tone)" "$tree_manifest"
expect_id "foliage.lighter_above"  "L4 catches pads no lighter above than below"    smoke "$(broken_tree no_gradient)" "$tree_manifest"
expect_id "foliage.bluer_below"    "L4 catches undersides darker but no bluer"      smoke "$(broken_tree grey_underside)" "$tree_manifest"
uses rock tree_1 smoke
expect_id "foliage.pieces"         "L4 catches foliage asked of an asset with none" smoke "$rock" "$(tamper 'm["foliage"] = json.load(open("'$tree_manifest'"))["foliage"]; m["foliage"]["material"] = "m_rock"' "$rock_manifest")"
uses tree_1 smoke paint tree_mutations
expect_id "painted.present"        "L4 catches bark and leaf on two copies of the texture" smoke "$(broken_tree two_textures)" "$tree_manifest"
expect_id "signed volume"          "L4 catches inside-out bark under open leaves"   smoke "$(broken_tree bark_inside_out)" "$tree_manifest"
# The core under the leaf pieces (ADR 9 as amended), and the bark's grain and close-range texels (ADR 12).
expect_id "foliage.cores"          "L4 catches pads with no core under their leaves" smoke "$(broken_tree no_cores)" "$tree_manifest"
expect_id "foliage.cores"          "L4 catches cores that are not closed"           smoke "$(broken_tree core_open)" "$tree_manifest"
expect_id "foliage.core_colour"    "L4 catches a core as light as the leaves"       smoke "$(broken_tree light_core)" "$tree_manifest"
expect_id "painted.grain"          "L4 catches bark with no grain"                  smoke "$(broken_tree no_grain)" "$tree_manifest"
expect_id "painted.grain_along"    "L4 catches grain running round the limbs"       smoke "$(broken_tree grain_across)" "$tree_manifest"
expect_id "uv.close_density"       "L4 catches a trunk with no more texels than a twig" smoke "$(broken_tree no_close_texels)" "$tree_manifest"
# Blades are foliage with no cores: the manifest asks for none, and the palette checks still hold.
uses blade_plant_1 smoke
expect 0 "L4 passes a plant of blades, which has no cores" smoke assets/models/blade_plant_1.glb assets/models/blade_plant_1.manifest.json
expect_id "foliage.palette" "L4 catches blades painted from another colour" smoke assets/models/blade_plant_1.glb "$(tamper 'm["materials"]["m_blade_leaf"][1] += 0.2' assets/models/blade_plant_1.manifest.json)"

# Overlapping pieces, painted (ADR 13): slab_1, two plates one pushed into the other.
uses slab_1 smoke
expect 0 "L4 passes the real slab"          smoke "$slab" "$slab_manifest"
# Three plates: the small one's sides stand close to the dominant one's, and counted as its exposed edges before a face of another piece counted as a join.
uses slab_2 smoke
expect 0 "L4 passes a slab of three plates" smoke assets/models/slab_2.glb assets/models/slab_2.manifest.json
uses slab_1 smoke paint slab_mutations
expect 0 "L4 passes an unbroken slab from the mutation script" smoke "$(broken_slab none)" "$slab_manifest"
expect_id "painted.crevices_darker" "L4 catches joins between pieces lit as exposed edges" smoke "$(broken_slab lit_joins)" "$slab_manifest"

# A table rock painted with its family's bands: its open faces are the neck's sides and the cap's, with air
# between, so the tones between the two are on no open face. That is no step in the texture (painted.banding).
uses table_rock_3 smoke
expect 0 "L4 passes a table rock whose open faces lie at two heights" smoke assets/models/table_rock_3.glb assets/models/table_rock_3.manifest.json

# A low stone (source/pebble): its open faces are its cap, almost all at one height, so the gradient
# from base to top is between its foot and its cap. pebble_1 from seed 1, unbroken and with one tint all the way up;
# that seed draws a stone of 104 triangles, which is all the manifest is changed to say.
uses pebble_1 smoke paint pebble_mutations
expect 0 "L4 passes an unbroken pebble whose open faces are all cap" smoke "$(broken_pebble flat_cap)" "$(tamper 'm["triangles"] = 104' assets/models/pebble_1.manifest.json)"
expect_id "painted.gradient" "L4 catches a pebble with no base-to-top gradient" smoke "$(broken_pebble no_gradient)" "$(tamper 'm["triangles"] = 104' assets/models/pebble_1.manifest.json)"

# The crevice shadow is asked of a shape with inside corners and of no other: a convex stone has nothing to
# measure it on, and a spec may leave it out only when the load test finds no inside corner either.
uses pebble_1 smoke
expect_id "painted.crevices_darker" "L4 catches a crevice shadow asked of a stone with no inside corner" smoke assets/models/pebble_1.glb "$(tamper 'm["painted"].update(crevice_shadow=0.45, crevice_width_m=0.012)' assets/models/pebble_1.manifest.json)"
uses rock smoke
expect_id "painted.crevices_darker" "L4 catches inside corners with no crevice shadow asked of them" smoke "$rock" "$(tamper 'del m["painted"]["crevice_shadow"], m["painted"]["crevice_width_m"]' "$rock_manifest")"

uses tracer smoke
expect 1 "L4 catches an unloadable file"    smoke "$(bad_glb)" "$manifest"

uses tracer view
expect 0 "L4b renders the real asset"       view "$glb" "$manifest" --screenshot "$tmp/shot.png"
expect 1 "L4b fails on an unloadable file"  view "$(bad_glb)" "$manifest" --screenshot "$tmp/bad.png"
expect 0 "L4b renders the asset's back"     view "$glb" "$manifest" --back --screenshot "$tmp/back.png"
# The manifest's bounds moved 300 m off: the camera frames empty ground, and no picture may be saved.
# Both cases read one run of the viewer (`away_view`).
expect_id "asset.in_picture" "L4b fails when the asset is not in the picture" away_view
expect 1 "L4b saves no picture without the asset in it" away_picture_exists

# L4c: bark seen from 0.5 m, as the gate takes it, with and without its grain.
uses tree_1 view_checks
expect 0 "L4c passes the real tree's bark"  view_checks tree_1 source/tree_1/review/final/bevy_trunk.png
uses tree_1 view_checks view paint tree_mutations
expect_id "view.bark_tone"  "L4c catches bark that is flat brown at arm's length" view_checks tree_1 "$(bark_shot no_grain)"
expect_id "view.bark_grain" "L4c catches grain seen running round the trunk" view_checks tree_1 "$(bark_shot grain_across)"

# L4d: a rock's sides turned away from the sun, in the viewer's picture, as the gate takes it.
uses slab_1 shade_check view paint slab_mutations
expect 0 "L4d passes an unbroken slab's shaded sides" shade_check slab_1 "$(shade_shot none)"
expect_id "view.shade_value" "L4d catches paint so dark the shaded sides are lost" shade_check slab_1 "$(shade_shot dark_paint)"
uses slab_1 shade_check
expect_id "view.shade_seen" "L4d catches a picture with no shaded side in it" shade_check slab_1 "$(shade_report 'r["away"]["pixels"] = 3')"

# A GLB that is valid glTF but outside the Bevy profile: Draco-compressed.
uses tracer bevy_lint
expect 0 "L2b passes the real export"       python tools/bevy_lint.py "$glb"
expect 1 "L2b catches Draco compression"    python tools/bevy_lint.py "$(exported draco)"
uses rock bevy_lint
expect 0 "L2b passes the real painted rock" python tools/bevy_lint.py "$rock"
uses rock bevy_lint paint rock_mutations
expect_id "images.decodable" "L2b catches a JPEG texture" python tools/bevy_lint.py "$(broken jpeg)"

# L0: a brief whose numbers disagree with its spec, and a spec number with no row in the brief.
# `lint_crate <sed expression>` lints a copy of the crate with that applied to its brief.
uses crate lint_spec
expect 0 "L0 passes a consistent brief"     lint_crate ''
expect 1 "L0 catches a brief/spec mismatch" lint_crate 's/| `recess_m.m_crate_panel` | `0.05` |/| `recess_m.m_crate_panel` | `0.03` |/'
expect 1 "L0 catches an untraced spec number" lint_crate '/`max_triangles`/d'
# L0, painted shading: the rock's spec with one thing wrong.
# `lint_rock <python>` lints a copy of the rock after that has changed its spec `s` and painted block `p`.
uses rock lint_spec
expect 0 "L0 passes the painted rock's spec"  lint_rock 'pass'
expect_id "spec.painted_shading"     "L0 catches a missing painted key"       lint_rock 'del p["edge_width_m"]'
expect_id "spec.painted_shading"     "L0 catches a colour that is not hex"    lint_rock 'p["growth"] = "moss green"'
expect_id "spec.painted_texture_px"  "L0 catches an odd texture size"         lint_rock 'p["texture_px"] = 1000'
expect_id "spec.painted_base_darker" "L0 catches a base lighter than the top" lint_rock 'p["base_tint"], p["top_tint"] = p["top_tint"], p["base_tint"]'
expect_id "spec.painted_amounts"     "L0 catches an impossible shadow amount" lint_rock 'p["crevice_shadow"] = 1.5'
expect_id "spec.painted_needs_uvs"   "L0 catches painted shading with no UVs" lint_rock 's["attributes"].remove("TEXCOORD_0")'
expect_id "spec.painted_shading"     "L0 catches a blotch with no size"       lint_rock 'del p["blotch_size_m"]'
expect_id "spec.painted_shading"     "L0 catches a crevice shadow with no width" lint_rock 'del p["crevice_width_m"]'
expect_id "spec.painted_shading"     "L0 catches growth placed with no growth colour" lint_rock 'del p["growth"], p["growth_height_m"]'
expect_id "spec.painted_amounts"     "L0 catches a side shade that leaves no light" lint_rock 'p["side_shade"] = 1.0'
expect_id "spec.fullness"            "L0 catches a fullness above the whole box" lint_rock 's["fullness"]["min_volume_share"] = 1.5'
expect_id "spec.painted_amounts"     "L0 catches growth darkened to black"    lint_rock 'p["growth_darker"] = 1.0'
expect_id "spec.pieces"              "L0 catches a pieces block with a key missing" lint_rock 'del s["pieces"]["min_step_ratio"]'
expect_id "spec.foot"                "L0 catches a foot on more sides than there are" lint_rock 's["foot"]["min_sides"] = 5'
expect_id "spec.chamfers"            "L0 catches a chamfer as big as a large plane" lint_rock 's["chamfers"]["min_m2"] = 0.5'
expect_id "spec.lean"                "L0 catches an upright share above the whole" lint_rock 's["lean"]["max_upright_share"] = 1.5'
expect_id "spec.planes"              "L0 catches a ledge's smaller plane set above a large one" lint_rock 's["planes"]["ledge_plane_m2"] = 0.9'
expect_id "spec.planes"              "L0 catches more ledge views than there are views" lint_rock 's["planes"]["min_ledge_views"] = 9'
expect_id "spec.painted_needs_uvs"   "L0 catches UVs on a flat-coloured asset" lint_rock 'del s["painted_shading"]'
# L0, overlapping pieces (ADR 13). The rock is one closed skin, so its copy is first stripped of the
# two blocks that measure one, and then says it is several pieces, with one thing wrong.
expect_id "spec.overlap"             "L0 catches an overlap block with a key missing" lint_rock 'del s["fullness"], s["pieces"]; s["overlap"] = {"min_count": 2, "max_count": 3, "max_buried_share": 0.3}'
expect_id "spec.overlap"             "L0 catches a buried share of the whole surface" lint_rock 'del s["fullness"], s["pieces"]; s["overlap"] = {"min_count": 2, "max_count": 3, "max_buried_share": 1.0, "min_step_ratio": 1.2}'
expect_id "spec.overlap"             "L0 catches overlapping pieces of which there need be only one" lint_rock 'del s["fullness"], s["pieces"]; s["overlap"] = {"min_count": 1, "max_count": 3, "max_buried_share": 0.3, "min_step_ratio": 1.2}'
expect_id "spec.overlap"             "L0 catches a size step that lets twins through" lint_rock 'del s["fullness"], s["pieces"]; s["overlap"] = {"min_count": 2, "max_count": 3, "max_buried_share": 0.3, "min_step_ratio": 0.9}'
expect_id "spec.one_skin_checks"     "L0 catches overlapping pieces measured as one closed skin" lint_rock 's["overlap"] = {"min_count": 2, "max_count": 3, "max_buried_share": 0.3, "min_step_ratio": 1.2}'
# L0, trees: tree_1's spec with one thing wrong. Its numbers come from its own brief and its family's.
# `lint_tree <python>` lints a copy of tree_1 after that has changed its spec `s`; `name` is the copy's own name.
uses tree_1 lint_spec
expect 0 "L0 passes a tree variant's spec"   lint_tree 'pass'
expect_id "brief.numbers_match_spec" "L0 catches a variant that disagrees with its family's brief" lint_tree 's["max_triangles"] = 6000'
expect_id "spec.family"              "L0 catches a family with no brief"       lint_tree 's["family"] = "zz_nope"'
expect_id "spec.open_materials"      "L0 catches an open material the asset does not have" lint_tree 's["open_materials"] = ["m_zz_nope"]'
expect_id "spec.foliage_amounts"     "L0 catches foliage that is not an open material" lint_tree 's["open_materials"] = []'
expect_id "spec.foliage"             "L0 catches a missing foliage key"        lint_tree 'del s["foliage"]["tones"]'
expect_id "spec.foliage_under_darker" "L0 catches an underside lighter than the top" lint_tree 'f=s["foliage"]; f["under_tint"], f["top_tint"] = f["top_tint"], f["under_tint"]'
expect_id "spec.foliage_needs_paint" "L0 catches foliage with no texture to take colour from" lint_tree 'del s["painted_shading"]; s["attributes"].remove("TEXCOORD_0")'
expect_id "spec.bark_darker"         "L0 catches bark lighter than the leaves" lint_tree 's["materials"]["m_tree_bark"] = "#e0e0d0"'
expect_id "spec.skeleton"            "L0 catches a missing skeleton key"       lint_tree 'del s["skeleton"]["min_roots"]'
expect_id "spec.skeleton_amounts"    "L0 catches a fork range given backwards" lint_tree 's["skeleton"]["fork_m"] = [3.5, 2.0]'
expect_id "spec.variants_amounts"    "L0 catches a variant listed as its own sibling" lint_tree 's["variants"]["siblings"] = [name]'
# The core, the lobes, the view from below and the bark's grain (ADR 9 as amended, ADR 12).
expect_id "spec.foliage_core_darker" "L0 catches a core lighter than the leaves' underside" lint_tree 's["foliage"]["core_tint"] = "#9fc0c8"'
expect_id "spec.foliage_core"        "L0 catches a lobe count given backwards" lint_tree 's["foliage"]["lobes"] = [4, 2]'
expect_id "spec.foliage_core"        "L0 catches more core seen than there is foliage" lint_tree 's["foliage"]["max_core_seen"] = 1.5'
expect_id "spec.foliage"             "L0 catches a missing limit on the view from below" lint_tree 'del s["foliage"]["max_seen_into"]'
expect_id "spec.painted_shading"     "L0 catches grain with no width"          lint_tree 'del s["painted_shading"]["grain_width_m"]'
expect_id "spec.painted_grain"       "L0 catches an impossible grain"          lint_tree 's["painted_shading"]["grain"] = 1.5'
expect_id "spec.painted_shading"     "L0 catches close texels with no height"  lint_tree 'del s["painted_shading"]["close_height_m"]'
expect_id "spec.painted_close"       "L0 catches close faces asked for fewer texels than any face gets" lint_tree 's["painted_shading"]["close_texels_per_m"] = 50.0'
expect_id "spec.skeleton_view"       "L0 catches grain in view asked to run across the trunk" lint_tree 's["skeleton"]["min_view_grain"] = 0.5'
# Species and growth stage (ADR 13): a tree's spec names a recipe and says how grown the tree is.
expect_id "spec.species"             "L0 catches a species with no recipe"     lint_tree 's["species"] = "zz_nope"'
expect_id "spec.species"             "L0 catches a tree with no species"       lint_tree 'del s["species"]'
expect_id "spec.growth_stage"        "L0 catches a growth stage older than the recipe draws" lint_tree 's["growth_stage"] = 5.0'
expect_id "spec.growth_stage"        "L0 catches a growth stage younger than the recipe draws" lint_tree 's["growth_stage"] = 0.3'
expect_id "spec.growth_stage"        "L0 catches a tree with no growth stage"  lint_tree 'del s["growth_stage"]'
expect_id "spec.growth_height"       "L0 catches a mature tree's height called a sapling" lint_tree 's["growth_stage"] = 0.5'
# Seasons (ADR 11, ADR 13): a season is another palette on its base asset's mesh, so its spec is the base's but for the palette.
# `lint_season <python>` lints a copy of tree_1_autumn after that has changed its spec `s`.
uses tree_1 tree_1_autumn lint_spec
expect 0 "L0 passes a season's spec"         lint_season 'pass'
expect_id "spec.season"              "L0 catches a season that is not one of the year's" lint_season 's["season"] = "monsoon"'
expect_id "spec.season"              "L0 catches a tree with no season"        lint_season 'del s["season"]'
expect_id "spec.palette_of"          "L0 catches a season drawn from another seed than its base" lint_season 's["seed"] = 2'
expect_id "spec.palette_of"          "L0 catches a season with a leaf shape of its own" lint_season 's["foliage"]["piece_m"] = [0.2, 0.9]'
expect_id "spec.palette_of"          "L0 catches a palette of an asset that does not exist" lint_season 's["palette_of"] = "zz_nope"'
expect_id "spec.palette_of"          "L0 catches a season in its base's own colours" lint_season 'b = json.load(open("source/tree_1/spec.json")); s["materials"] = b["materials"]; s["foliage"] = b["foliage"]'

# L2c: a season's GLB carries its base's mesh, UVs included: only the texture differs.
uses tree_1 tree_1_autumn same_mesh
expect 0 "L2c passes a season on its base's mesh" python tools/same_mesh.py assets/models/tree_1_autumn.glb assets/models/tree_1.glb
uses tree_1 tree_2 same_mesh
expect_id "palette.same_mesh"        "L2c catches a season on another tree's mesh" python tools/same_mesh.py assets/models/tree_2.glb assets/models/tree_1.glb
uses tree_1 tree_1_autumn same_mesh paint tree_mutations
expect_id "palette.same_mesh"        "L2c catches a season whose leaves sit on other swatches" python tools/same_mesh.py "$(broken_tree gradient_within_piece)" assets/models/tree_1.glb
uses tree_1 same_mesh
expect_id "palette.other_texture"    "L2c catches a season with its base's own texture" python tools/same_mesh.py assets/models/tree_1.glb assets/models/tree_1.glb
# L0, blades: blade_plant_1's spec with one thing wrong, and a tree's with blades added.
# `lint_blade <python>` lints a copy of blade_plant_1 after that has changed its spec `s`.
uses blade_plant_1 lint_spec
expect 0 "L0 passes a blade plant's spec"    lint_blade 'pass'
expect_id "spec.blades"              "L0 catches a missing blades key"         lint_blade 'del s["blades"]["min_arch"]'
expect_id "spec.blades_amounts"      "L0 catches a lean range given backwards" lint_blade 's["blades"]["lean_deg"] = [85.0, 15.0]'
expect_id "spec.blades_amounts"      "L0 catches a blade wider than it is long" lint_blade 's["blades"]["width_share"] = [0.08, 1.5]'
expect_id "spec.foliage"             "L0 catches a canopy's keys on a plant of blades" lint_blade 's["foliage"]["lobes"] = [1, 2]'
expect_id "spec.blades_need_foliage" "L0 catches blades with no foliage to be" lint_blade 'del s["foliage"]; s["open_materials"] = []'
uses tree_1 lint_spec
expect_id "spec.foliage"             "L0 catches blades asked of a canopy"     lint_tree 's["blades"] = {"width_share": [0.08, 0.25], "root_m": 0.15, "max_gap_deg": 100.0, "lean_deg": [15.0, 85.0], "min_arch": 0.08}'

# L0, slabs: slab_1's spec with one thing wrong. Its numbers come from its own brief and its family's.
uses slab_1 lint_spec
expect 0 "L0 passes a slab variant's spec"   lint_slab 'pass'
expect_id "spec.top"                 "L0 catches a level share above the whole view" lint_slab 's["top"]["min_level_share"] = 1.5'
expect_id "spec.overlap"             "L0 catches a slab asked for more pieces at least than at most" lint_slab 's["overlap"]["min_count"] = 4'
expect_id "spec.painted_joins"       "L0 catches overlapping pieces with no crevice shadow to hide their joins" lint_slab 'del s["painted_shading"]["crevice_shadow"], s["painted_shading"]["crevice_width_m"]'
expect_id "spec.one_skin_checks"     "L0 catches a slab's fullness asked as if it were one skin" lint_slab 's["fullness"] = {"min_volume_share": 0.3, "min_crown_share": 0.2}'
# L0, crags: crag_1's spec with one thing wrong in what it asks of its prisms (`cluster`).
# L0, a pebble (source/pebble): low and rounded, each a share below 1.
uses pebble_2 lint_spec
expect 0 "L0 passes a pebble variant's spec" lint_pebble 'pass'
expect_id "spec.low"                 "L0 catches a pebble allowed to be as tall as it is wide" lint_pebble 's["low"]["max_height_share"] = 1.0'
expect_id "spec.rounded"             "L0 catches a steep plane allowed the whole surface" lint_pebble 's["rounded"]["max_steep_plane_share"] = 1.0'
expect_id "brief.numbers_match_spec" "L0 catches a pebble's spec without the family's limit on height" lint_pebble 'del s["low"]'
uses crag_1 lint_spec
expect 0 "L0 passes a crag variant's spec"   lint_crag 'pass'
expect_id "spec.cluster"             "L0 catches a height step that lets prisms of one height through" lint_crag 's["cluster"]["max_height_step"] = 1.0'
expect_id "spec.cluster"             "L0 catches a crag asked for one prism" lint_crag 's["cluster"]["min_prisms"] = 1'
expect_id "spec.cluster"             "L0 catches a lean spread of the whole compass" lint_crag 's["cluster"]["max_lean_spread_deg"] = 180.0'
expect_id "spec.cluster"             "L0 catches a cluster block with a key missing" lint_crag 'del s["cluster"]["min_lean_deg"]'
expect_id "spec.cluster"             "L0 catches prisms asked of one closed skin" lint_crag 'del s["overlap"]'
# L0, blocks: block_2's spec with one thing wrong in what it asks of its box (`block`) and its crack (`cracks`).
uses block_2 lint_spec
expect 0 "L0 passes a block variant's spec"  lint_block 'pass'
expect_id "spec.block"               "L0 catches a square share above the whole outline" lint_block 's["block"]["min_square_share"] = 1.5'
expect_id "spec.block"               "L0 catches a block asked for chamfers of no width" lint_block 's["block"]["min_chamfer_m"] = 0.0'
expect_id "spec.block"               "L0 catches a block block with a key missing" lint_block 'del s["block"]["min_chamfers"]'
expect_id "spec.cracks"              "L0 catches a block asked for no cracks at all" lint_block 's["cracks"]["count"] = 0'
expect_id "spec.cracks"              "L0 catches a crack of no depth" lint_block 's["cracks"]["depth_m"] = 0.0'
expect_id "spec.cracks"              "L0 catches a crack that need cross none of the block" lint_block 's["cracks"]["min_span"] = 0.0'
expect_id "spec.cracks"              "L0 catches cracks asked of something that is not a block" lint_block 'del s["block"]'

# L5b: a sheet never approved, an approved sheet, then the approved sheet with something drawn on it.
# `baseline_check <state>` puts a copy of the tracer's sheet in that state and checks it.
uses tracer baseline
expect 0 "L5b passes when never approved"   baseline_check never_approved
expect 0 "L5b passes an unchanged sheet"    baseline_check approved
expect 1 "L5b catches a changed sheet"      baseline_check drawn_on

# L5c: a sheet saved as viewers show it, then the same sheet 16 bits deep with alpha, which they band.
uses rock image_lint
expect 0 "L5c passes the real sheet"        python tools/image_lint.py source/rock/review/final/sheet.png
expect_id "image.eight_bit" "L5c catches a 16-bit sheet"        python tools/image_lint.py "$(sheet_as PNG48 -depth 16)"
expect_id "image.opaque"    "L5c catches a sheet with alpha"    python tools/image_lint.py "$(sheet_as PNG32 -alpha on)"
# The review aids are review images too.
uses rock image_lint review_aids
expect 0 "L5c passes a review aid"          python tools/image_lint.py "$(review_aid views)"
expect 0 "L5c passes a blind comparison"    python tools/image_lint.py "$(review_aid blind)"
# L0, table rocks: table_rock_1's spec with one thing wrong in what it asks of its cap and necks (`table`).
uses table_rock_1 lint_spec
expect 0 "L0 passes a table rock variant's spec" lint_table 'pass'
expect_id "spec.table"               "L0 catches a clearance above the table rock's own height" lint_table 's["table"]["min_clear_m"] = 5.0'
expect_id "spec.table"               "L0 catches necks allowed to fill the outline" lint_table 's["table"]["max_neck_share"] = 1.0'
expect_id "spec.table"               "L0 catches a table block with a key missing" lint_table 'del s["table"]["min_overhang_m"]'
expect_id "spec.table"               "L0 catches a table rock with more necks than pieces under its cap" lint_table 's["table"]["necks"] = 3'
expect_id "spec.table"               "L0 catches a cap and necks asked of one closed skin" lint_table 'del s["overlap"]'
