use graph_engine::Engine;
use std::time::Instant;

fn main() {
    for &n in &[1000usize, 5000, 20000] {
        let m = n * 2;
        let mut e = Engine::default();
        if std::env::var("NOCOL").is_ok() { e.params.collision = 0.0; }
        e.init(n, m);
        if std::env::var("NOCOL").is_ok() { e.params.collision = 0.0; }
        for i in 0..n {
            let a = i as f32 * 2.4;
            let r = (i as f32).sqrt() * 10.0;
            e.pos[2 * i] = a.cos() * r;
            e.pos[2 * i + 1] = a.sin() * r;
        }
        for k in 0..m {
            e.edges[2 * k] = (k % n) as u32;
            e.edges[2 * k + 1] = ((k * 7 + 1) % n) as u32;
        }
        let t = Instant::now();
        for _ in 0..20 {
            e.step(1.0, 1.0);
        }
        println!("n={n:6} m={m:6}: {:.2} ms/step", t.elapsed().as_secs_f64() * 1000.0 / 20.0);
    }
}
