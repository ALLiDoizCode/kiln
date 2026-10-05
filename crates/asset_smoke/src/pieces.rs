//! Overlapping pieces (ADR 13): an asset may be several closed pieces that pass into each
//! other, each softened on its own. They stay separate in the mesh, so they are read back
//! from the loaded triangles: triangles that share a corner position are one piece.

use std::collections::HashMap;

use bevy::prelude::*;

/// Which piece each triangle belongs to, numbered from 0, and how many pieces there are.
pub fn split(triangles: &[[Vec3; 3]]) -> (Vec<usize>, usize) {
    // The exporter splits a vertex wherever its normal or UV differs, and copies the position
    // exactly, so corners at one place have the same bits.
    let mut at: HashMap<[u32; 3], usize> = HashMap::new();
    let mut parent: Vec<usize> = (0..triangles.len()).collect();
    fn root(parent: &mut [usize], mut i: usize) -> usize {
        while parent[i] != i {
            parent[i] = parent[parent[i]];
            i = parent[i];
        }
        i
    }
    for (index, triangle) in triangles.iter().enumerate() {
        for corner in triangle {
            let key = corner.to_array().map(f32::to_bits);
            let other = *at.entry(key).or_insert(index);
            let (a, b) = (root(&mut parent, index), root(&mut parent, other));
            parent[a] = b;
        }
    }
    let mut number: HashMap<usize, usize> = HashMap::new();
    let pieces = (0..triangles.len())
        .map(|index| {
            let found = root(&mut parent, index);
            let next = number.len();
            *number.entry(found).or_insert(next)
        })
        .collect();
    (pieces, number.len())
}

/// The volume each piece encloses: positive when its triangles face outward.
pub fn volumes(triangles: &[[Vec3; 3]], piece: &[usize], count: usize) -> Vec<f32> {
    let mut volumes = vec![0.0; count];
    for ([a, b, c], piece) in triangles.iter().zip(piece) {
        volumes[*piece] += a.dot(b.cross(*c)) / 6.0;
    }
    volumes
}

/// Whether a point is inside any piece other than `own`: the space there is solid rock, and a
/// surface with that just in front of it is buried and never seen.
pub fn buried(point: Vec3, own: usize, triangles: &[[Vec3; 3]], piece: &[usize], count: usize) -> bool {
    // Not along any axis or likely face: a ray along a face, or through an edge, counts wrongly.
    let ray = Vec3::new(0.137, 0.947, 0.291).normalize();
    let mut crossings = vec![0u32; count];
    for ([a, b, c], piece) in triangles.iter().zip(piece) {
        if *piece == own {
            continue;
        }
        // Möller and Trumbore: where the ray from the point meets the triangle's plane, in the triangle's own coordinates.
        let (ab, ac) = (*b - *a, *c - *a);
        let p = ray.cross(ac);
        let det = ab.dot(p);
        if det.abs() < 1e-12 {
            continue;
        }
        let from = point - *a;
        let u = from.dot(p) / det;
        let q = from.cross(ab);
        let v = ray.dot(q) / det;
        if u >= 0.0 && v >= 0.0 && u + v <= 1.0 && ac.dot(q) / det > 0.0 {
            crossings[*piece] += 1;
        }
    }
    crossings.iter().any(|n| n % 2 == 1)
}
