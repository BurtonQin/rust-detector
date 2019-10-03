struct P {
    a: i32,
}

struct S {
    x: Option<P>,
}

impl S {
    fn peek(&self) -> Option<&P> {
        return self.x.as_ref();
    }

    fn pop(&self) -> Option<P> {
        unsafe {
            let p = self as *const Self as *mut Self;
            return (*p).x.take();
        }
    }
}

fn main() {
    let s: S = S { x: Some( P { a: 1 } )};
    let p1 = s.peek().unwrap();
    let p2 = s.pop().unwrap();
    println!("{}, {}", p1.a, p2.a);
}
