<script>
  const API_BASE = '/api'; // vite proxy → localhost:8000

  let unitcell = 'A15';
  let repNx = 2;
  let repNy = 2;
  let repNz = 2;
  let assessCages = true;
  let density = 0.8;
  let shiftX = 0.1;
  let shiftY = 0.1;
  let shiftZ = 0.1;

  let loading = false;
  let error = null;
  let pdb = null;
  let waterCount = null;
  let cages = null;
  let viewerContainer;
  let viewer = null;

  async function generate() {
    loading = true;
    error = null;
    pdb = null;

    try {
      const unitcell_options = {
        shift: [shiftX, shiftY, shiftZ],
        density,
        assess_cages: assessCages,
      };

      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          unitcell,
          rep: [repNx, repNy, repNz],
          unitcell_options,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || res.statusText);
      }

      const data = await res.json();
      pdb = data.pdb;
      waterCount = data.water_count;
      cages = data.cages;
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function doResize() {
    if (viewer?.resize && viewerContainer) {
      viewer.resize();
    }
  }

  const BOND_CUTOFF = 3.0; // 3Å以内の酸素対に水素結合を描画
  const BOND_RADIUS = 0.08; // 辺の太さ（円柱の半径）
  const HOVER_ATOM_COLOR = 'orange';
  const BOND_COLOR = 'lightblue';
  const HOVER_BOND_COLOR = 'darkorange';

  let bondSpecs = []; // 3Dmolに渡すspec（shapeと同一参照になる想定）

  function addDistanceBonds(v) {
    bondSpecs = [];
    const model = v.getModel(0);
    if (!model) return;
    const atoms = model.selectedAtoms({});
    for (let i = 0; i < atoms.length; i++) {
      for (let j = i + 1; j < atoms.length; j++) {
        const a = atoms[i];
        const b = atoms[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dz = b.z - a.z;
        const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (d <= BOND_CUTOFF && d > 0.1) {
          const spec = {
            start: { x: a.x, y: a.y, z: a.z },
            end: { x: b.x, y: b.y, z: b.z },
            radius: BOND_RADIUS,
            color: BOND_COLOR,
            fromCap: 'round',
            toCap: 'round',
            hoverable: true,
            hover_callback(shape, viewer) {
              shape.color = HOVER_BOND_COLOR;
              viewer.render();
            },
            unhover_callback(shape, viewer) {
              shape.color = BOND_COLOR;
              viewer.render();
            },
          };
          bondSpecs.push(spec);
          v.addCylinder(spec);
        }
      }
    }
  }

  function revertBondColors() {
    bondSpecs.forEach((s) => { s.color = BOND_COLOR; });
    if (viewer) viewer.render();
  }

  function setupAtomHover(v) {
    v.setHoverable(
      {},
      true,
      (atom) => {
        v.setStyle({ serial: atom.serial }, { sphere: { scale: 0.3, color: HOVER_ATOM_COLOR } });
        v.render();
      },
      (atom) => {
        v.setStyle({ serial: atom.serial }, { sphere: { scale: 0.25 } });
        v.render();
      }
    );
  }

  $: if (pdb && viewerContainer) {
    const initViewer = () => {
      if (viewer) {
        viewer.clear();
        viewer.addModel(pdb, 'pdb', { assignBonds: false });
      } else {
        viewer = window.$3Dmol.createViewer(viewerContainer, {
          backgroundColor: 'white',
          defaultView: true,
          hoverDuration: 80, // ホバー検出の遅延を短く（デフォルト500ms）
        });
        viewer.addModel(pdb, 'pdb', { assignBonds: false });
        // コンテナのリサイズを監視してviewerを合わせる
        const ro = new ResizeObserver(() => doResize());
        ro.observe(viewerContainer);
      }
      addDistanceBonds(viewer);
      viewer.setStyle({}, { sphere: { scale: 0.25 } });
      setupAtomHover(viewer);
      // ビューワー外にマウスが出たときに辺の色を戻す（unhoverが呼ばれない対策）
      viewerContainer.onmouseleave = revertBondColors;
      viewer.zoomTo();
      viewer.render();
      // レイアウト確定後にresizeしてコンテナ内に収める
      requestAnimationFrame(() => {
        setTimeout(doResize, 0);
      });
    };
    if (window.$3Dmol) {
      initViewer();
    } else if (window.$3Dmolpromise) {
      window.$3Dmolpromise.then(initViewer);
    }
  }
</script>

<main>
  <header>
    <h1>GenIce Studio</h1>
    <p>結晶骨格の可視化（酸素＋水素結合）</p>
  </header>

  <div class="layout">
    <section class="form">
      <h2>パラメータ</h2>
      <form onsubmit={(e) => { e.preventDefault(); generate(); }}>
        <label>
          単位胞
          <input type="text" bind:value={unitcell} placeholder="1h, A15, CS1..." />
        </label>
        <div class="rep">
          <label> rep
            <input type="number" min="1" max="16" bind:value={repNx} />
            <input type="number" min="1" max="16" bind:value={repNy} />
            <input type="number" min="1" max="16" bind:value={repNz} />
          </label>
        </div>
        <label>
          <input type="checkbox" bind:checked={assessCages} />
          assess_cages
        </label>
        <label>
          density
          <input type="number" step="0.01" bind:value={density} />
        </label>
        <div class="shift">
          <label> shift
            <input type="number" step="0.01" bind:value={shiftX} />
            <input type="number" step="0.01" bind:value={shiftY} />
            <input type="number" step="0.01" bind:value={shiftZ} />
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? '生成中...' : '生成'}
        </button>
      </form>
      {#if error}
        <p class="error">{error}</p>
      {/if}
      {#if waterCount !== null}
        <p class="info">水分子数: {waterCount}{#if cages} / ケージ: {Object.keys(cages).length}{/if}</p>
      {/if}
    </section>

    <section class="viewer">
      <h2>3D表示</h2>
      <div
        bind:this={viewerContainer}
        class="mol-viewer viewer_3Dmoljs"
        role="img"
        aria-label="分子構造"
      ></div>
    </section>
  </div>
</main>

<style>
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
    font-family: system-ui, sans-serif;
  }
  header {
    margin-bottom: 1.5rem;
  }
  h1 {
    font-size: 1.5rem;
    margin: 0;
  }
  h2 {
    font-size: 1rem;
    margin: 0 0 0.5rem;
  }
  .layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 1.5rem;
  }
  @media (max-width: 700px) {
    .layout {
      grid-template-columns: 1fr;
    }
  }
  .form {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 8px;
    height: fit-content;
  }
  form label {
    display: block;
    margin-bottom: 0.75rem;
    font-size: 0.9rem;
  }
  form input[type='text'],
  form input[type='number'] {
    display: block;
    width: 100%;
    padding: 0.35rem 0.5rem;
    margin-top: 0.2rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  .rep input,
  .shift input {
    width: 4rem;
    display: inline-block;
    margin-right: 0.25rem;
  }
  button {
    margin-top: 0.5rem;
    padding: 0.5rem 1rem;
    background: #333;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  button:hover:not(:disabled) {
    background: #555;
  }
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .error {
    color: #c00;
    font-size: 0.9rem;
    margin-top: 0.5rem;
  }
  .info {
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.5rem;
  }
  .viewer {
    min-height: 400px;
    position: relative;
  }
  .mol-viewer {
    position: relative;
    width: 100%;
    height: 500px;
    min-height: 400px;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
  }
</style>
