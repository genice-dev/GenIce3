- ion dope の場合、システム上、Na とかを指定したら、Na 分子をさがしにいってしまうが、ないのでエラーになる。ion dope の場合には、ない分子を指定されても受けいれるようにする必要がある。パーザーを分けるべきか?

現在の呼びだし方法。

```
python3 -m genice3.cli.genice "A15[shift=(0.1,0.1,0.1), anion.0=me, cation.6=me, density=0.8]"   --rep 2 2 2  --exporter "gromacs[guest.A12=me, guest.A14=et, spot_guest.0=4site, water=4site]" -D
```
