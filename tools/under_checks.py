"""Gate L4e: a tree's canopy as a player under it sees it, measured in a Bevy screenshot.

The gate takes the picture with `asset_view --stand 1 --pitch 78`: a player's
eye 1 m from the trunk, looking up into the canopy. What each pixel shows is
not guessed from its colour (under a canopy bark and leaf are both dark): the
same camera is set up over the built asset here, a ray is cast through every
second pixel, and the face it meets says whether the pixel is bark, a leaf
piece, a core or sky, and which way the side seen faces. A sample counts only
when its eight neighbours show the same kind, so no edge is measured.

The typical tone of a kind is read from samples whose seen side faces away
from the viewer's sun: the light cannot reach them, so they show their colour
under the ambient light alone, which is how the underside of a canopy is lit.

- view.under_seen: the picture is that view of this asset: where the rays
  meet the tree the picture is not sky, and where they meet nothing it is.
- view.under_pale: no leaf piece shows the sun's glare. A piece shows one of
  the palette's colours, lighter or darker as the light falls; glare is the
  light's colour and not the leaf's, so it is grey where every swatch is a
  hue. A sample of a leaf piece is pale when it is nearer grey than halfway
  from the palette's greyest swatch to white (greyness: its least channel
  over its greatest) and lighter than `pale_light` times the typical unlit
  piece. At most `max_pale_share` of the samples may be. A glossy leaf
  material fails it: a flat piece the sun grazes, seen from under it, shows
  the sun and none of its own colour, near-white among dark neighbours. A
  palette that is itself near white (winter's snow) cannot be told from glare
  this way and the limit then says so; a season is its base's mesh and
  material (gate L2c), and the base is gated first.
- view.under_limbs: foliage seen from below (pieces and cores) is lighter
  than the limbs among it (bark above the lowest leaf) by `skeleton.min_canopy_over_limbs`, so limbs
  stand out against the canopy.

Usage: tools/bl tools/under_checks.py <asset> <screenshot.png> [--of <asset whose built mesh the picture shows>]
"""

import json
import math
import statistics
import sys
from pathlib import Path

import bmesh
import bpy
import numpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import foliage
from pipeline import Asset, Checks, conventions, linear_rgb, script_args

# The viewer's camera and sun (crates/asset_view/src/main.rs: STAND_FOV, the directional light). They are
# written twice; `view.under_seen` fails when the two disagree, because the rays then miss what the picture shows.
FOV = 1.31
TO_SUN = Vector((-0.4, -0.6, 1.0)).normalized()  # Bevy's (0.4, -1, -0.6) is where the light goes; +Z up here
STRIDE_PX = 2
LUMA = numpy.array((0.2126, 0.7152, 0.0722))
SKY, BARK, PIECE, CORE, TRUNK = range(5)


def linear(values):
    return numpy.where(values <= 0.04045, values / 12.92, ((values + 0.055) / 1.055) ** 2.4)


def picture(path):
    """The screenshot as linear RGB, row 0 at the top."""
    image = bpy.data.images.load(str(path))
    width, height = image.size
    pixels = numpy.empty(width * height * 4, dtype=numpy.float32)
    image.pixels.foreach_get(pixels)
    bpy.data.images.remove(image)
    return linear(pixels.reshape(height, width, 4)[::-1, :, :3].astype(numpy.float64))


def seen(obj, cores, bark_slot, floor, eye, forward, size):
    """What a ray through every `STRIDE_PX`th pixel meets: (kind, whether the side seen faces away from the sun), as grids.

    Bark below `floor`, the lowest foliage, is the trunk and not a limb among the leaves: a kind of its own."""
    right = forward.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(forward)
    half = math.tan(FOV / 2)
    count = size // STRIDE_PX
    kind = numpy.full((count, count), SKY, dtype=numpy.int8)
    unlit = numpy.zeros((count, count), dtype=bool)
    for row in range(count):
        y = 1 - (row * STRIDE_PX + 0.5) / size * 2
        for column in range(count):
            x = (column * STRIDE_PX + 0.5) / size * 2 - 1
            direction = (forward + right * (x * half) + up * (y * half)).normalized()
            hit, location, normal, index = obj.ray_cast(eye, direction)
            if not hit:
                continue
            polygon = obj.data.polygons[index]
            if polygon.material_index == bark_slot and location.z < floor:
                kind[row, column] = TRUNK
                continue
            kind[row, column] = BARK if polygon.material_index == bark_slot else CORE if index in cores else PIECE
            facing = normal if normal.dot(direction) < 0 else -normal
            unlit[row, column] = facing.dot(TO_SUN) < -0.1
    return kind, unlit


def sky_share(tree, at, stand, pitch, eye_height, cells=128):
    """The share of the view from under a tree that is sky, from its geometry alone: `tree` is a BVH of the whole mesh, `at` the trunk's place.

    The same eye, direction and field of view as `measure`, on a coarser grid, and as there a sample counts only when
    its neighbours are sky too. source/tree/generator.py asks it of a tree before keeping it: `view.under_seen` cannot
    read a picture that holds no sky."""
    eye = Vector((at[0] + stand / math.sqrt(2), at[1] - stand / math.sqrt(2), eye_height))
    forward = Vector((-math.cos(pitch) / math.sqrt(2), math.cos(pitch) / math.sqrt(2), math.sin(pitch)))
    right = forward.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(forward)
    half = math.tan(FOV / 2)
    sky = numpy.zeros((cells, cells), dtype=bool)
    for row in range(cells):
        y = 1 - (row + 0.5) / cells * 2
        for column in range(cells):
            x = (column + 0.5) / cells * 2 - 1
            sky[row, column] = tree.ray_cast(eye, (forward + right * (x * half) + up * (y * half)).normalized())[2] is None
    return float(inner(sky).sum() / sky.size)


def inner(mask):
    """A grid of booleans with every cell dropped that has a neighbour outside it."""
    padded = numpy.pad(mask, 1, constant_values=False)
    out = mask.copy()
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            out &= padded[dy : dy + mask.shape[0], dx : dx + mask.shape[1]]
    return out


def measure(name, shot, stand, pitch):
    """The view from under `name`'s built mesh, read from the screenshot `shot`."""
    asset = Asset(name)
    result = bpy.ops.wm.open_mainfile(filepath=str(asset.blend))
    if result != {"FINISHED"}:
        raise RuntimeError(f"open failed: {result}")
    spec = asset.spec()
    obj = bpy.data.objects[spec["objects"][0]]
    bpy.context.view_layer.update()
    names = [slot.material.name for slot in obj.material_slots]
    leaf_slot, bark_slot = names.index(spec["foliage"]["material"]), names.index(spec["skeleton"]["material"])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.index_update()
    cores = {face.index for core in foliage.cores_of(bm, leaf_slot) for face in core}
    floor = min(v.co.z for face in bm.faces if face.material_index == leaf_slot for v in face.verts)
    bm.free()

    with open(asset.manifest) as f:
        at = json.load(f)["stand_at"]  # (x, z) in Bevy's axes
    eye_height = conventions()["metrics"]["eye_height_m"]
    eye = Vector((at[0] + stand / math.sqrt(2), -at[1] - stand / math.sqrt(2), eye_height))
    forward = Vector((-math.cos(pitch) / math.sqrt(2), math.cos(pitch) / math.sqrt(2), math.sin(pitch)))
    rgb = picture(shot)
    size = rgb.shape[0]
    kind, unlit = seen(obj, cores, bark_slot, floor, eye, forward, size)
    light = (rgb @ LUMA)[::STRIDE_PX, ::STRIDE_PX][: kind.shape[0], : kind.shape[1]]
    colour = rgb[::STRIDE_PX, ::STRIDE_PX][: kind.shape[0], : kind.shape[1]]

    sky = inner(kind == SKY)
    tree = inner(kind != SKY)
    found = {"sky_samples": int(sky.sum()), "tree_samples": int(tree.sum())}
    if sky.sum():
        # The sky's colour is the typical colour where the rays meet nothing.
        backdrop = numpy.median(colour[sky], axis=0)
        like_sky = numpy.abs(colour - backdrop).max(axis=2) < 0.02
        found["sky_is_sky"] = float(like_sky[sky].mean())
        found["tree_is_sky"] = float(like_sky[tree].mean()) if tree.sum() else 1.0
    every_piece = inner(kind == PIECE)
    pieces = light[every_piece & unlit]
    grey = colour.min(axis=2) / numpy.maximum(colour.max(axis=2), 1e-6)
    found.update(every_piece=int(every_piece.sum()), piece_light=light[every_piece], piece_grey=grey[every_piece])
    canopy = light[inner((kind == PIECE) | (kind == CORE)) & unlit]
    bark = light[inner(kind == BARK) & unlit]
    found.update(piece_samples=len(pieces), bark_samples=len(bark))
    if len(pieces):
        found["piece"] = float(numpy.median(pieces))
        found["canopy"] = float(numpy.median(canopy))
    if len(bark):
        found["bark"] = float(numpy.median(bark))
    return found, spec


if __name__ == "__main__":
    args = script_args()
    name, shot = args[0], Path(args[1])
    rules = conventions()["under_view"]
    found, spec = measure(args[args.index("--of") + 1] if "--of" in args else name, shot, rules["stand_m"], math.radians(rules["pitch_deg"]))
    want = Asset(name).spec()["foliage"]
    limbs = Asset(name).spec()["skeleton"]["min_canopy_over_limbs"]
    palette = foliage.palette(linear_rgb(Asset(name).spec()["materials"][want["material"]]), linear_rgb(want["under_tint"]), linear_rgb(want["top_tint"]), want["shades"], want["tones"], want["variation"])
    # Greyness: a colour's least channel over its greatest. The limit is halfway from the palette's greyest swatch to white.
    greyest = max(min(colour) / max(colour) for row in palette for colour in row)
    grey_limit = (greyest + 1) / 2

    checks = Checks("L4e-under", name)
    in_view = (
        found["sky_samples"] >= rules["min_samples"]
        and found["piece_samples"] >= rules["min_samples"]
        and found["bark_samples"] >= rules["min_samples"]
        and found["sky_is_sky"] >= rules["min_agree"]
        and found["tree_is_sky"] <= 1 - rules["min_agree"]
    )
    checks.check(
        "view.under_seen",
        in_view,
        f"{shot} is not this tree from {rules['stand_m']} m looking {rules['pitch_deg']} degrees up: rays meet sky at {found['sky_samples']} samples, unlit leaf pieces at {found['piece_samples']} and unlit bark at {found['bark_samples']} "
        f"(need {rules['min_samples']} of each); the picture shows sky at {found.get('sky_is_sky', 0):.3f} of the sky samples and at {found.get('tree_is_sky', 1):.3f} of the tree's (need {rules['min_agree']} and at most {1 - rules['min_agree']:.2f})",
    )
    if in_view:
        light_limit = found["piece"] * rules["pale_light"]
        pale = float(((found["piece_grey"] > grey_limit) & (found["piece_light"] > light_limit)).mean())
        over = found["canopy"] / found["bark"]
        print(
            f"{name} from below in {shot.name}: {found['every_piece']} samples of leaf pieces, {found['piece_samples']} of them and {found['bark_samples']} of limbs seen from the unlit side; "
            f"the typical unlit piece has luminance {found['piece']:.4f}; {pale:.5f} of the piece samples are pale (greyness over {grey_limit:.2f}, the palette's greyest swatch {greyest:.2f}, and lighter than {light_limit:.4f}); "
            f"foliage {found['canopy']:.4f} over limbs {found['bark']:.4f} is {over:.2f}"
        )
        checks.check(
            "view.under_pale",
            pale <= rules["max_pale_share"],
            f"from below, {pale:.5f} of {found['every_piece']} samples of leaf pieces are pale: nearer grey than {grey_limit:.2f} (the palette's greyest swatch is {greyest:.2f}) and lighter than {light_limit:.4f}, "
            f"{rules['pale_light']} times the typical unlit piece; at most {rules['max_pale_share']} may be: that is the sun's glare and not a leaf's colour (a glossy leaf material)",
        )
        checks.check(
            "view.under_limbs",
            over >= limbs,
            f"from below, foliage seen from its unlit side has luminance {found['canopy']:.4f} and bark {found['bark']:.4f}: {over:.2f} times; spec wants at least {limbs}, so that limbs stand out against the canopy",
        )
    else:
        checks.check("view.under_pale", False, "not measured: the picture is not this view of this tree")
        checks.check("view.under_limbs", False, "not measured: the picture is not this view of this tree")
    checks.finish(Asset(name).report("L4e-under"))
