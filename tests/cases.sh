# The cases of tests/run.sh: every check must be able to fail.
#
# One case per line, and nothing else but comments and `uses` lines. A case is
#   expect <exit code> "<name>" <command...>      the command must exit with that code
#   expect_id "<check id>" "<name>" <command...>  the command must exit 1 and name that check
# Its name starts with its gate (L0, L1, L2b, L4, L4b, L4c, L5b, L5c) and is unique.
# `uses <tag...>` says what the cases below it depend on, until the next `uses`: the assets they
# read, and the tools behind them (see `tags_of_file` in tests/run.sh). Selection goes by these.
#
# tests/run.sh runs each line in a shell of its own, in any order and several at once, so a case
# may not depend on another: it writes only under its own "$tmp", and anything two cases share
# is a fixture (`broken`, `broken_tree`, `exported`, `flipped_normals`, `bark_shot`, `once`), built once by whichever
# case asks first. The helpers are in tests/run.sh.

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
