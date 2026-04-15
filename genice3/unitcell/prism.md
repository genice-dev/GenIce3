# Mapping Fractional Coordinates onto a Cylinder

On a square lattice, the basis vectors are $(1,0)$ and $(0,1)$.  
In fractional coordinates, these correspond to `dfx` and `dfy`.

Let the circumferential and axial components of `dfx` be $c_x$ and $a_x$, respectively.

Likewise, let the circumferential and axial components of `dfy` be $c_y$ and $a_y$.

Assume a target cylinder with radius $R$ and axial length scale $L$, and let the target bond length be $p$.

First, consider `dfx`. If the initial point is $(R,0,0)$, then the point displaced by `dfx` is
$(R\cos 2\pi c_x,\; R\sin 2\pi c_x,\; La_x)$.

We require the distance between these two points to be $p$:

$$R^2(1-\cos 2\pi c_x)^2+R^2\sin^2 2\pi c_x+L^2a_x^2=p^2$$

Similarly,

$$R^2(1-\cos 2\pi c_y)^2+R^2\sin^2 2\pi c_y+L^2a_y^2=p^2$$

Solve these two equations simultaneously to obtain $R$ and $L$.
