//! The review pictures as data: which pictures are taken, and where the camera stands for each.
//!
//! This is the one place the set is written down in code. `learn/reference/review-pictures.html`
//! says the same in words. Change anything here that moves a camera, and [`VIEW_SET`] goes up by
//! one, so that an asset record says which set its pictures were taken with.
//!
//! Everything here is plain arithmetic on the model's bounding box: no Bevy app is needed to test it.
//!
//! Axes are glTF's, which Bevy shares: +Y is up and the front of a model faces +Z. A camera in
//! front of the model therefore stands on +Z and looks towards -Z.

use bevy::math::Vec3;

/// The number of this set of pictures. Pictures taken with different numbers cannot be compared.
pub const VIEW_SET: u32 = 1;

/// Every picture's width and height in pixels: the screen the pit profile was measured at.
pub const PICTURE_SIZE: (u32, u32) = (1920, 1080);

/// The height of a standing player's eye above the ground, in metres.
pub const EYE_HEIGHT: f32 = 1.7;
/// The player's vertical field of view in degrees, used for the pictures taken as a player sees.
pub const PLAYER_FOV: f32 = 72.0;
/// The vertical field of view in degrees of the pictures that hold the whole asset: narrow, so
/// that the near parts of the asset are not drawn much larger than the far parts.
pub const WHOLE_FOV: f32 = 30.0;
/// How far the camera of a picture taken straight along an axis stands from the middle of the
/// bounding box, in sizes. At 2.5 sizes a box as large as the size in every dimension just fits.
pub const AXIS_DISTANCE: f32 = 2.5;
/// The same for the picture taken from a corner, where the box's diagonal has to fit.
pub const CORNER_DISTANCE: f32 = 3.5;
/// How far the `standing` picture's camera is from the front of the bounding box, in metres.
pub const STANDING_DISTANCE: f32 = 2.0;
/// The post drawn beside the asset in the `standing` picture: its height (a player's), its
/// width and depth, and the gap between it and the bounding box. In metres.
pub const POST_HEIGHT: f32 = 1.8;
pub const POST_WIDTH: f32 = 0.3;
pub const POST_GAP: f32 = 0.3;

/// Where a picture's camera stands.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Stand {
    /// The whole asset: the camera is `sizes` times the size from the middle of the bounding
    /// box, in the direction `from`, looking at that middle.
    Whole { from: Vec3, sizes: f32 },
    /// As a player standing in front of the asset sees it: the eye at [`EYE_HEIGHT`] above the
    /// ground, [`STANDING_DISTANCE`] out from the front of the bounding box, looking at its
    /// middle. A post of a player's height stands beside the asset.
    Standing,
    /// At the target profile's closest viewing distance: the eye that far out from the front of
    /// the bounding box, looking level and straight at it, at [`EYE_HEIGHT`] or at the middle of
    /// the asset's height if that is lower.
    Closest,
}

/// One of the review pictures.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct View {
    /// The picture's file name without `.png`. Shape review and final review use the same names.
    pub name: &'static str,
    /// What the picture shows, for a person reading a list of them.
    pub shows: &'static str,
    pub stand: Stand,
}

const fn whole(name: &'static str, shows: &'static str, from: Vec3, sizes: f32) -> View {
    View { name, shows, stand: Stand::Whole { from, sizes } }
}

/// The set, in the order the pictures are taken and listed.
pub const VIEWS: [View; 8] = [
    whole("front", "the front (+Z side), whole asset", Vec3::Z, AXIS_DISTANCE),
    whole("right", "the side on the right of the front picture (+X side), whole asset", Vec3::X, AXIS_DISTANCE),
    whole("back", "the back (-Z side), whole asset", Vec3::NEG_Z, AXIS_DISTANCE),
    whole("left", "the side on the left of the front picture (-X side), whole asset", Vec3::NEG_X, AXIS_DISTANCE),
    whole("top", "from straight above, the front towards the bottom of the picture", Vec3::Y, AXIS_DISTANCE),
    // Half way between front and right, 30 degrees above level: (sin 45 cos 30, sin 30, cos 45 cos 30).
    whole(
        "three_quarter",
        "from the front right corner, 30 degrees above level, whole asset",
        Vec3::new(0.612_372_4, 0.5, 0.612_372_4),
        CORNER_DISTANCE,
    ),
    View {
        name: "standing",
        shows: "as a player standing 2 m in front sees it, beside a post 1.8 m tall",
        stand: Stand::Standing,
    },
    View {
        name: "closest",
        shows: "as a player sees it at the target profile's closest viewing distance",
        stand: Stand::Closest,
    },
];

/// How the model as its file has it is put in front of the cameras: multiplied by `scale`, then
/// moved by `translation`. The file itself is never written to.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Placing {
    pub scale: f32,
    pub translation: Vec3,
    /// The placed bounding box's width (X), height (Y) and depth (Z) in metres. Its largest is
    /// the size. The placed box stands on the ground (Y = 0) with its middle over the origin.
    pub extent: Vec3,
}

/// Places a model whose bounding box in the file runs from `min` to `max` so that its largest
/// dimension is `size` metres, it stands on the ground, and its middle is over the origin.
/// `None` if the box has no extent, so there is nothing to scale.
pub fn placing(min: Vec3, max: Vec3, size: f32) -> Option<Placing> {
    let largest = (max - min).max_element();
    if !(largest > 0.0 && largest.is_finite() && size > 0.0) {
        return None;
    }
    let scale = size / largest;
    let middle = (min + max) / 2.0;
    Some(Placing {
        scale,
        translation: Vec3::new(-middle.x, -min.y, -middle.z) * scale,
        extent: (max - min) * scale,
    })
}

/// Where a camera is and what it looks at.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Shot {
    pub eye: Vec3,
    pub looks_at: Vec3,
    /// The direction that is up in the picture.
    pub up: Vec3,
    /// Vertical field of view in degrees.
    pub fov: f32,
    /// Nothing nearer the eye than this is drawn. In metres.
    pub near: f32,
}

/// The camera for one view of a placed model. `size` is the run's size in metres and `closest`
/// the target profile's closest viewing distance in metres.
pub fn shot(view: &View, placed: &Placing, size: f32, closest: f32) -> Shot {
    let middle = Vec3::new(0.0, placed.extent.y / 2.0, 0.0);
    let front = placed.extent.z / 2.0;
    let (eye, looks_at, up, fov) = match view.stand {
        Stand::Whole { from, sizes } => {
            let from = from.normalize();
            // Looking straight down, "up" in the picture is away from the front.
            let up = if from.y.abs() > 0.999 { Vec3::NEG_Z } else { Vec3::Y };
            (middle + from * sizes * size, middle, up, WHOLE_FOV)
        }
        Stand::Standing => (Vec3::new(0.0, EYE_HEIGHT, front + STANDING_DISTANCE), middle, Vec3::Y, PLAYER_FOV),
        Stand::Closest => {
            let eye = Vec3::new(0.0, EYE_HEIGHT.min(middle.y), front + closest);
            (eye, eye + Vec3::NEG_Z, Vec3::Y, PLAYER_FOV)
        }
    };
    // Near enough that a small asset seen from close is not cut away, and never beyond Bevy's 0.1 m.
    let reach = match view.stand {
        Stand::Closest => closest,
        _ => eye.distance(middle),
    };
    Shot { eye, looks_at, up, fov, near: (reach * 0.05).clamp(1e-4, 0.1) }
}

/// The middle of the post that stands beside a placed model in the `standing` picture: to the
/// right of the bounding box as the front picture shows it, level with the box's middle in depth.
pub fn post_middle(placed: &Placing) -> Vec3 {
    Vec3::new(placed.extent.x / 2.0 + POST_GAP + POST_WIDTH / 2.0, POST_HEIGHT / 2.0, 0.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn close(a: Vec3, b: Vec3) -> bool {
        a.distance(b) < 1e-5
    }

    fn view(name: &str) -> &'static View {
        VIEWS.iter().find(|v| v.name == name).unwrap()
    }

    /// A model 2 wide, 4 high and 1 deep in its file, off to one side and above the ground.
    fn tall() -> Placing {
        placing(Vec3::new(10.0, 3.0, -6.0), Vec3::new(12.0, 7.0, -5.0), 0.8).unwrap()
    }

    #[test]
    fn the_names_are_distinct_and_fit_file_names() {
        for (i, v) in VIEWS.iter().enumerate() {
            assert!(v.name.chars().all(|c| c.is_ascii_lowercase() || c == '_'), "{}", v.name);
            assert!(VIEWS[..i].iter().all(|other| other.name != v.name), "{} twice", v.name);
            assert!(!v.shows.is_empty());
        }
    }

    #[test]
    fn exactly_one_picture_is_at_the_closest_viewing_distance() {
        assert_eq!(VIEWS.iter().filter(|v| v.stand == Stand::Closest).count(), 1);
    }

    #[test]
    fn placing_makes_the_largest_dimension_the_size_on_the_ground_over_the_origin() {
        let placed = tall();
        assert!((placed.scale - 0.2).abs() < 1e-6);
        assert!(close(placed.extent, Vec3::new(0.4, 0.8, 0.2)));
        // The corners of the file's box, placed.
        let low = Vec3::new(10.0, 3.0, -6.0) * placed.scale + placed.translation;
        let high = Vec3::new(12.0, 7.0, -5.0) * placed.scale + placed.translation;
        assert!(close(low, Vec3::new(-0.2, 0.0, -0.1)), "{low}");
        assert!(close(high, Vec3::new(0.2, 0.8, 0.1)), "{high}");
    }

    #[test]
    fn a_model_with_no_extent_or_a_size_of_nothing_cannot_be_placed() {
        assert!(placing(Vec3::ONE, Vec3::ONE, 0.8).is_none());
        assert!(placing(Vec3::MAX, Vec3::MIN, 0.8).is_none());
        assert!(placing(Vec3::ZERO, Vec3::ONE, 0.0).is_none());
        assert!(placing(Vec3::ZERO, Vec3::ONE, f32::NAN).is_none());
    }

    #[test]
    fn whole_views_stand_a_set_number_of_sizes_from_the_middle_on_their_own_side() {
        let placed = tall();
        let middle = Vec3::new(0.0, 0.4, 0.0);
        for (name, eye) in [
            ("front", Vec3::new(0.0, 0.4, 2.0)),
            ("right", Vec3::new(2.0, 0.4, 0.0)),
            ("back", Vec3::new(0.0, 0.4, -2.0)),
            ("left", Vec3::new(-2.0, 0.4, 0.0)),
            ("top", Vec3::new(0.0, 2.4, 0.0)),
        ] {
            let shot = shot(view(name), &placed, 0.8, 0.5);
            assert!(close(shot.eye, eye), "{name}: {}", shot.eye);
            assert!(close(shot.looks_at, middle), "{name}");
            assert_eq!(shot.fov, WHOLE_FOV);
        }
        let corner = shot(view("three_quarter"), &placed, 0.8, 0.5);
        assert!((corner.eye.distance(middle) - 2.8).abs() < 1e-5);
        assert!(corner.eye.x > 0.0 && corner.eye.z > 0.0, "front right");
        assert!((corner.eye.x - corner.eye.z).abs() < 1e-5, "half way between front and right");
        let rise = ((corner.eye.y - middle.y) / 2.8).asin().to_degrees();
        assert!((rise - 30.0).abs() < 1e-3, "{rise}");
    }

    #[test]
    fn the_distance_follows_the_size_and_not_the_shape() {
        let flat = placing(Vec3::ZERO, Vec3::new(5.0, 0.1, 5.0), 2.0).unwrap();
        let thin = placing(Vec3::ZERO, Vec3::new(0.1, 5.0, 0.1), 2.0).unwrap();
        for v in VIEWS.iter().filter(|v| matches!(v.stand, Stand::Whole { .. })) {
            let (a, b) = (shot(v, &flat, 2.0, 0.5), shot(v, &thin, 2.0, 0.5));
            assert!((a.eye.distance(a.looks_at) - b.eye.distance(b.looks_at)).abs() < 1e-5, "{}", v.name);
        }
    }

    #[test]
    fn looking_straight_down_the_front_is_at_the_bottom_of_the_picture() {
        let top = shot(view("top"), &tall(), 0.8, 0.5);
        assert_eq!(top.up, Vec3::NEG_Z);
        assert_eq!(shot(view("front"), &tall(), 0.8, 0.5).up, Vec3::Y);
    }

    /// Whether a point is inside the picture of a shot, by the angles to it from the eye.
    fn in_frame(shot: &Shot, point: Vec3) -> bool {
        let forward = (shot.looks_at - shot.eye).normalize();
        let right = forward.cross(shot.up).normalize();
        let up = right.cross(forward);
        let to = point - shot.eye;
        let depth = to.dot(forward);
        let half = (shot.fov.to_radians() / 2.0).tan();
        let aspect = PICTURE_SIZE.0 as f32 / PICTURE_SIZE.1 as f32;
        depth > shot.near && (to.dot(up) / depth).abs() <= half && (to.dot(right) / depth).abs() <= half * aspect
    }

    #[test]
    fn every_whole_view_holds_every_corner_of_any_box_of_the_size() {
        for extent in [Vec3::ONE, Vec3::new(1.0, 0.05, 1.0), Vec3::new(0.05, 1.0, 0.3), Vec3::new(0.2, 0.5, 1.0)] {
            for size in [0.01, 0.8, 12.5] {
                let placed = placing(Vec3::ZERO, extent, size).unwrap();
                for v in VIEWS.iter().filter(|v| matches!(v.stand, Stand::Whole { .. })) {
                    let shot = shot(v, &placed, size, 0.5);
                    for corner in 0..8 {
                        let pick = |bit: u32, low: f32, high: f32| if corner & bit == 0 { low } else { high };
                        let half = placed.extent / 2.0;
                        let point = Vec3::new(
                            pick(1, -half.x, half.x),
                            pick(2, 0.0, placed.extent.y),
                            pick(4, -half.z, half.z),
                        );
                        assert!(in_frame(&shot, point), "{} of {extent} at size {size}: {point}", v.name);
                    }
                }
            }
        }
    }

    #[test]
    fn the_closest_view_is_the_closest_viewing_distance_from_the_front_of_the_box() {
        let placed = tall(); // 0.8 high, 0.2 deep: its front face is at z = 0.1
        let shot = shot(view("closest"), &placed, 0.8, 0.5);
        assert!(close(shot.eye, Vec3::new(0.0, 0.4, 0.6)), "{}", shot.eye);
        assert!(close(shot.looks_at - shot.eye, Vec3::NEG_Z), "level, straight at the front");
        assert_eq!(shot.fov, PLAYER_FOV);
        assert!(shot.near < 0.5);
        // Another profile's distance moves the eye and nothing else.
        let further = super::shot(view("closest"), &placed, 0.8, 1.25);
        assert!(close(further.eye, Vec3::new(0.0, 0.4, 1.35)));
    }

    #[test]
    fn the_closest_view_is_at_eye_height_once_the_asset_is_tall_enough() {
        let wall = placing(Vec3::ZERO, Vec3::new(4.0, 6.0, 0.5), 6.0).unwrap();
        let shot = shot(view("closest"), &wall, 6.0, 0.5);
        assert!(close(shot.eye, Vec3::new(0.0, EYE_HEIGHT, 0.75)), "{}", shot.eye);
    }

    #[test]
    fn the_standing_view_is_a_players_eye_two_metres_out_with_the_post_in_the_picture() {
        let placed = tall();
        let shot = shot(view("standing"), &placed, 0.8, 0.5);
        assert!(close(shot.eye, Vec3::new(0.0, 1.7, 2.1)), "{}", shot.eye);
        assert!(close(shot.looks_at, Vec3::new(0.0, 0.4, 0.0)));
        assert_eq!(shot.fov, PLAYER_FOV);
        let post = post_middle(&placed);
        assert!(close(post, Vec3::new(0.65, 0.9, 0.0)), "{post}");
        for y in [0.0, POST_HEIGHT] {
            assert!(in_frame(&shot, Vec3::new(post.x, y, post.z)));
        }
    }

    #[test]
    fn the_near_limit_shrinks_with_a_small_asset() {
        let placed = placing(Vec3::ZERO, Vec3::ONE, 0.01).unwrap();
        let shot = shot(view("front"), &placed, 0.01, 0.5);
        assert!(shot.near < shot.eye.distance(shot.looks_at) - 0.01, "{}", shot.near);
        let big = placing(Vec3::ZERO, Vec3::ONE, 12.5).unwrap();
        assert_eq!(super::shot(view("front"), &big, 12.5, 0.5).near, 0.1);
    }
}
