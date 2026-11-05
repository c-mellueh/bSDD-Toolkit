//! Force-directed graph layout for the bSDD Toolkit web graph viewer.
//!
//! Compiled to `wasm32-unknown-unknown` without wasm-bindgen: the host allocates
//! buffers through `init`, writes node/edge data directly into WebAssembly memory
//! (pointers returned by the `*_ptr` functions) and calls `step` repeatedly.
//!
//! Forces:
//! * repulsion between all nodes (Coulomb, Barnes-Hut approximation, O(n log n))
//! * springs along edges (Hooke, rest length per edge)
//! * gravity towards the centre
//! * collision: extra push when nodes overlap (radius per node)
//! Integration is a damped velocity-Verlet with a speed limit and an "alpha"
//! cooling factor supplied by the host.

use std::cell::RefCell;

#[derive(Clone, Copy)]
pub struct Params {
    pub repulsion: f32,
    pub spring_length: f32,
    pub spring_k: f32,
    pub gravity: f32,
    pub damping: f32,
    pub theta: f32,
    pub max_speed: f32,
    pub collision: f32,
}

impl Default for Params {
    fn default() -> Self {
        Params { repulsion: 1200.0, spring_length: 90.0, spring_k: 0.04, gravity: 0.02, damping: 0.6, theta: 0.8, max_speed: 60.0, collision: 1.0 }
    }
}

#[derive(Default)]
pub struct Engine {
    pub n: usize,
    pub m: usize,
    pub pos: Vec<f32>,     // x0,y0,x1,y1,...
    pub vel: Vec<f32>,     // vx0,vy0,...
    pub force: Vec<f32>,   // scratch
    pub fixed: Vec<u8>,    // 1 = pinned
    pub mass: Vec<f32>,    // repulsion weight
    pub radius: Vec<f32>,  // collision radius
    pub edges: Vec<u32>,   // s0,t0,s1,t1,...
    pub rest: Vec<f32>,    // rest length factor per edge
    pub strength: Vec<f32>,// spring strength factor per edge
    pub params: Params,
    tree: Vec<Quad>,
}

#[derive(Clone, Copy)]
struct Quad {
    cx: f32,
    cy: f32,
    half: f32,
    mass: f32,
    mx: f32, // mass-weighted sum (centre of mass = mx / mass)
    my: f32,
    body: i32,       // single body index, -1 if none / internal
    child: [i32; 4], // -1 = empty
    leaf: bool,
    size2: f32,
}

impl Quad {
    fn new(cx: f32, cy: f32, half: f32) -> Quad {
        Quad { cx, cy, half, mass: 0.0, mx: 0.0, my: 0.0, body: -1, child: [-1; 4], leaf: true, size2: 0.0 }
    }
}

const MAX_DEPTH: u32 = 40;

impl Engine {
    pub fn init(&mut self, n: usize, m: usize) {
        self.n = n;
        self.m = m;
        self.pos = vec![0.0; n * 2];
        self.vel = vec![0.0; n * 2];
        self.force = vec![0.0; n * 2];
        self.fixed = vec![0; n];
        self.mass = vec![1.0; n];
        self.radius = vec![20.0; n];
        self.edges = vec![0; m * 2];
        self.rest = vec![1.0; m];
        self.strength = vec![1.0; m];
        self.tree = Vec::with_capacity(n * 4 + 1);
    }

    fn build_tree(&mut self) {
        self.tree.clear();
        if self.n == 0 {
            return;
        }
        let (mut x0, mut y0, mut x1, mut y1) = (f32::MAX, f32::MAX, f32::MIN, f32::MIN);
        for i in 0..self.n {
            let (x, y) = (self.pos[2 * i], self.pos[2 * i + 1]);
            if !x.is_finite() || !y.is_finite() {
                continue;
            }
            x0 = x0.min(x);
            y0 = y0.min(y);
            x1 = x1.max(x);
            y1 = y1.max(y);
        }
        if x0 > x1 {
            x0 = 0.0;
            y0 = 0.0;
            x1 = 1.0;
            y1 = 1.0;
        }
        let half = ((x1 - x0).max(y1 - y0) * 0.5).max(1.0) + 1.0;
        self.tree.push(Quad::new((x0 + x1) * 0.5, (y0 + y1) * 0.5, half));
        for i in 0..self.n {
            let (x, y) = (self.pos[2 * i], self.pos[2 * i + 1]);
            if x.is_finite() && y.is_finite() {
                self.insert(0, i, x, y, 0);
            }
        }
        for q in self.tree.iter_mut() {
            if q.mass > 0.0 {
                q.mx /= q.mass;
                q.my /= q.mass;
            }
            q.leaf = q.child.iter().all(|&c| c < 0);
            q.size2 = (q.half * 2.0) * (q.half * 2.0);
        }
    }

    fn quadrant(q: &Quad, x: f32, y: f32) -> usize {
        ((x >= q.cx) as usize) | (((y >= q.cy) as usize) << 1)
    }

    fn child_of(&mut self, qi: usize, k: usize) -> usize {
        let c = self.tree[qi].child[k];
        if c >= 0 {
            return c as usize;
        }
        let q = self.tree[qi];
        let h = q.half * 0.5;
        let cx = if k & 1 == 1 { q.cx + h } else { q.cx - h };
        let cy = if k & 2 == 2 { q.cy + h } else { q.cy - h };
        self.tree.push(Quad::new(cx, cy, h));
        let idx = self.tree.len() - 1;
        self.tree[qi].child[k] = idx as i32;
        idx
    }

    fn insert(&mut self, qi: usize, i: usize, x: f32, y: f32, depth: u32) {
        let w = self.mass[i];
        {
            let q = &mut self.tree[qi];
            q.mass += w;
            q.mx += x * w;
            q.my += y * w;
        }
        let is_leaf = self.tree[qi].child.iter().all(|&c| c < 0);
        if is_leaf {
            if self.tree[qi].body < 0 && self.tree[qi].mass == w {
                self.tree[qi].body = i as i32;
                return;
            }
            if depth >= MAX_DEPTH {
                // degenerate: coincident points, keep aggregated mass only
                self.tree[qi].body = -1;
                return;
            }
            let old = self.tree[qi].body;
            self.tree[qi].body = -1;
            if old >= 0 {
                let o = old as usize;
                let (ox, oy) = (self.pos[2 * o], self.pos[2 * o + 1]);
                let k = Self::quadrant(&self.tree[qi], ox, oy);
                let c = self.child_of(qi, k);
                self.insert(c, o, ox, oy, depth + 1);
            }
        }
        let k = Self::quadrant(&self.tree[qi], x, y);
        let c = self.child_of(qi, k);
        self.insert(c, i, x, y, depth + 1);
    }

    fn repulse(&mut self, i: usize) {
        let (x, y) = (self.pos[2 * i], self.pos[2 * i + 1]);
        let wi = self.mass[i] * self.params.repulsion;
        let theta2 = self.params.theta * self.params.theta;
        let (mut fx, mut fy) = (0.0f32, 0.0f32);
        let mut stack: [u32; 256] = [0; 256];
        let mut sp = 1usize;
        let me = i as i32;
        let tree = &self.tree;
        while sp > 0 {
            sp -= 1;
            let q = &tree[stack[sp] as usize];
            if q.mass <= 0.0 {
                continue;
            }
            let dx = x - q.mx;
            let dy = y - q.my;
            let d2 = dx * dx + dy * dy;
            if q.leaf || q.size2 < theta2 * d2 {
                if q.leaf && q.body == me {
                    continue;
                }
                if d2 < 0.01 {
                    // coincident: deterministic nudge
                    let a = (i as f32) * 2.399_963;
                    fx += a.cos() * wi * q.mass;
                    fy += a.sin() * wi * q.mass;
                    continue;
                }
                // f = rep * wi * m / d^2, direction (dx,dy)/d  =>  (dx,dy) * f / d
                let inv = wi * q.mass / (d2 * d2.sqrt());
                fx += dx * inv;
                fy += dy * inv;
            } else {
                for &c in q.child.iter() {
                    if c >= 0 && sp < 256 {
                        stack[sp] = c as u32;
                        sp += 1;
                    }
                }
            }
        }
        self.force[2 * i] += fx;
        self.force[2 * i + 1] += fy;
    }

    /// One simulation step. Returns the mean speed (useful to detect convergence).
    pub fn step(&mut self, dt: f32, alpha: f32) -> f32 {
        let n = self.n;
        if n == 0 {
            return 0.0;
        }
        for f in self.force.iter_mut() {
            *f = 0.0;
        }
        self.build_tree();
        for i in 0..n {
            self.repulse(i);
        }
        // springs
        let p = self.params;
        for e in 0..self.m {
            let s = self.edges[2 * e] as usize;
            let t = self.edges[2 * e + 1] as usize;
            if s >= n || t >= n || s == t {
                continue;
            }
            let dx = self.pos[2 * t] - self.pos[2 * s];
            let dy = self.pos[2 * t + 1] - self.pos[2 * s + 1];
            let d = (dx * dx + dy * dy).sqrt().max(0.01);
            let rest = p.spring_length * self.rest[e] + (self.radius[s] + self.radius[t]) * 0.5;
            let f = p.spring_k * self.strength[e] * (d - rest);
            let (fx, fy) = (dx / d * f, dy / d * f);
            self.force[2 * s] += fx;
            self.force[2 * s + 1] += fy;
            self.force[2 * t] -= fx;
            self.force[2 * t + 1] -= fy;
        }
        // centre of mass for gravity
        let (mut gx, mut gy) = (0.0f32, 0.0f32);
        for i in 0..n {
            gx += self.pos[2 * i];
            gy += self.pos[2 * i + 1];
        }
        gx /= n as f32;
        gy /= n as f32;
        let mut speed_sum = 0.0f32;
        let damping = p.damping.clamp(0.0, 0.99);
        let limit = p.max_speed;
        for i in 0..n {
            if self.fixed[i] != 0 {
                self.vel[2 * i] = 0.0;
                self.vel[2 * i + 1] = 0.0;
                continue;
            }
            let x = self.pos[2 * i];
            let y = self.pos[2 * i + 1];
            let fx = self.force[2 * i] - (x - gx) * p.gravity * self.mass[i];
            let fy = self.force[2 * i + 1] - (y - gy) * p.gravity * self.mass[i];
            let inv = 1.0 / self.mass[i].max(0.1);
            let mut vx = (self.vel[2 * i] + fx * inv * dt * alpha) * (1.0 - damping);
            let mut vy = (self.vel[2 * i + 1] + fy * inv * dt * alpha) * (1.0 - damping);
            let sp = (vx * vx + vy * vy).sqrt();
            if sp > limit {
                vx = vx / sp * limit;
                vy = vy / sp * limit;
            }
            if !vx.is_finite() || !vy.is_finite() {
                vx = 0.0;
                vy = 0.0;
            }
            self.vel[2 * i] = vx;
            self.vel[2 * i + 1] = vy;
            self.pos[2 * i] = x + vx * dt;
            self.pos[2 * i + 1] = y + vy * dt;
            speed_sum += sp.min(limit);
        }
        if p.collision > 0.0 {
            self.collide(p.collision);
        }
        speed_sum / n as f32
    }

    /// Resolve overlaps with a uniform grid (counting sort, O(n) on average).
    fn collide(&mut self, strength: f32) {
        let n = self.n;
        let mut cell = 1.0f32;
        for r in self.radius.iter() {
            cell = cell.max(*r * 2.0);
        }
        let (mut x0, mut y0, mut x1, mut y1) = (f32::MAX, f32::MAX, f32::MIN, f32::MIN);
        for i in 0..n {
            x0 = x0.min(self.pos[2 * i]);
            y0 = y0.min(self.pos[2 * i + 1]);
            x1 = x1.max(self.pos[2 * i]);
            y1 = y1.max(self.pos[2 * i + 1]);
        }
        if !(x0.is_finite() && y0.is_finite() && x1.is_finite() && y1.is_finite()) {
            return;
        }
        // keep the grid size bounded
        let max_cells = (n * 4).max(64) as f32;
        while ((x1 - x0) / cell + 1.0) * ((y1 - y0) / cell + 1.0) > max_cells {
            cell *= 2.0;
        }
        let w = ((x1 - x0) / cell) as usize + 1;
        let h = ((y1 - y0) / cell) as usize + 1;
        let cells = w * h;
        let mut start = vec![0u32; cells + 1];
        let mut cell_of = vec![0u32; n];
        for i in 0..n {
            let cx = ((self.pos[2 * i] - x0) / cell) as usize;
            let cy = ((self.pos[2 * i + 1] - y0) / cell) as usize;
            let c = cy.min(h - 1) * w + cx.min(w - 1);
            cell_of[i] = c as u32;
            start[c + 1] += 1;
        }
        for c in 0..cells {
            start[c + 1] += start[c];
        }
        let mut fill = start.clone();
        let mut order = vec![0u32; n];
        for i in 0..n {
            let c = cell_of[i] as usize;
            order[fill[c] as usize] = i as u32;
            fill[c] += 1;
        }
        for i in 0..n {
            let c = cell_of[i] as usize;
            let (cx, cy) = ((c % w) as isize, (c / w) as isize);
            for oy in -1..=1isize {
                let yy = cy + oy;
                if yy < 0 || yy >= h as isize {
                    continue;
                }
                for ox in -1..=1isize {
                    let xx = cx + ox;
                    if xx < 0 || xx >= w as isize {
                        continue;
                    }
                    let k = yy as usize * w + xx as usize;
                    for idx in start[k]..start[k + 1] {
                        let j = order[idx as usize] as usize;
                        if j <= i {
                            continue;
                        }
                        let dx = self.pos[2 * j] - self.pos[2 * i];
                        let dy = self.pos[2 * j + 1] - self.pos[2 * i + 1];
                        let min = self.radius[i] + self.radius[j];
                        let d2 = dx * dx + dy * dy;
                        if d2 >= min * min || d2 == 0.0 {
                            continue;
                        }
                        let d = d2.sqrt();
                        let push = (min - d) / d * 0.5 * strength;
                        let (px, py) = (dx * push, dy * push);
                        match (self.fixed[i] != 0, self.fixed[j] != 0) {
                            (false, false) => {
                                self.pos[2 * i] -= px;
                                self.pos[2 * i + 1] -= py;
                                self.pos[2 * j] += px;
                                self.pos[2 * j + 1] += py;
                            }
                            (true, false) => {
                                self.pos[2 * j] += 2.0 * px;
                                self.pos[2 * j + 1] += 2.0 * py;
                            }
                            (false, true) => {
                                self.pos[2 * i] -= 2.0 * px;
                                self.pos[2 * i + 1] -= 2.0 * py;
                            }
                            _ => {}
                        }
                    }
                }
            }
        }
    }
}

// ---------------------------------------------------------------- C ABI for WebAssembly

thread_local! {
    static ENGINE: RefCell<Engine> = RefCell::new(Engine::default());
}

#[no_mangle]
pub extern "C" fn init(n: u32, m: u32) {
    ENGINE.with(|e| e.borrow_mut().init(n as usize, m as usize));
}

macro_rules! ptr_fn {
    ($name:ident, $field:ident, $t:ty) => {
        #[no_mangle]
        pub extern "C" fn $name() -> *mut $t {
            ENGINE.with(|e| e.borrow_mut().$field.as_mut_ptr())
        }
    };
}

ptr_fn!(pos_ptr, pos, f32);
ptr_fn!(vel_ptr, vel, f32);
ptr_fn!(fixed_ptr, fixed, u8);
ptr_fn!(mass_ptr, mass, f32);
ptr_fn!(radius_ptr, radius, f32);
ptr_fn!(edges_ptr, edges, u32);
ptr_fn!(rest_ptr, rest, f32);
ptr_fn!(strength_ptr, strength, f32);

#[no_mangle]
#[allow(clippy::too_many_arguments)]
pub extern "C" fn set_params(repulsion: f32, spring_length: f32, spring_k: f32, gravity: f32, damping: f32, theta: f32, max_speed: f32, collision: f32) {
    ENGINE.with(|e| {
        e.borrow_mut().params = Params { repulsion, spring_length, spring_k, gravity, damping, theta, max_speed, collision };
    });
}

#[no_mangle]
pub extern "C" fn step(dt: f32, alpha: f32) -> f32 {
    ENGINE.with(|e| e.borrow_mut().step(dt, alpha))
}

/// Run `count` steps at once, returns the mean speed of the last one.
#[no_mangle]
pub extern "C" fn steps(count: u32, dt: f32, alpha: f32) -> f32 {
    ENGINE.with(|e| {
        let mut eng = e.borrow_mut();
        let mut s = 0.0;
        for _ in 0..count {
            s = eng.step(dt, alpha);
        }
        s
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn engine(n: usize, edges: &[(u32, u32)]) -> Engine {
        let mut e = Engine::default();
        e.init(n, edges.len());
        for i in 0..n {
            let a = i as f32 * 0.7;
            e.pos[2 * i] = a.cos() * (i as f32);
            e.pos[2 * i + 1] = a.sin() * (i as f32);
        }
        for (k, (s, t)) in edges.iter().enumerate() {
            e.edges[2 * k] = *s;
            e.edges[2 * k + 1] = *t;
        }
        e
    }

    #[test]
    fn nodes_separate_and_converge() {
        let mut e = engine(50, &[(0, 1), (1, 2), (2, 3)]);
        for _ in 0..500 {
            e.step(1.0, 1.0);
        }
        // no NaN and nodes are spread out
        assert!(e.pos.iter().all(|v| v.is_finite()));
        let d = ((e.pos[0] - e.pos[2]).powi(2) + (e.pos[1] - e.pos[3]).powi(2)).sqrt();
        assert!(d > 20.0 && d < 400.0, "spring distance {d}");
        let speed = e.step(1.0, 0.05);
        assert!(speed < 5.0, "speed {speed}");
    }

    #[test]
    fn pinned_nodes_do_not_move() {
        let mut e = engine(10, &[(0, 1)]);
        e.fixed[0] = 1;
        let (x, y) = (e.pos[0], e.pos[1]);
        for _ in 0..50 {
            e.step(1.0, 1.0);
        }
        assert_eq!((e.pos[0], e.pos[1]), (x, y));
    }

    #[test]
    fn coincident_nodes_are_separated() {
        let mut e = engine(20, &[]);
        for v in e.pos.iter_mut() {
            *v = 0.0;
        }
        for _ in 0..100 {
            e.step(1.0, 1.0);
        }
        assert!(e.pos.iter().all(|v| v.is_finite()));
        assert!((e.pos[0] - e.pos[2]).abs() + (e.pos[1] - e.pos[3]).abs() > 1.0);
    }
}
