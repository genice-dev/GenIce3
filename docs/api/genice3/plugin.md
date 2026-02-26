    <main class="pdoc">
            <section class="module-info">
                    <h1 class="modulename">
genice3<wbr>.plugin    </h1>

                        <div class="docstring"><p>Plugin handler.</p>
</div>

                        <input id="mod-plugin-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">

                        <label class="view-source-button" for="mod-plugin-view-source"><span>View Source</span></label>

                        <div class="pdoc-code codehilite"><pre><span></span><span id="L-1"><a href="#L-1"><span class="linenos">  1</span></a><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-2"><a href="#L-2"><span class="linenos">  2</span></a><span class="sd">Plugin handler.</span>
</span><span id="L-3"><a href="#L-3"><span class="linenos">  3</span></a><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-4"><a href="#L-4"><span class="linenos">  4</span></a>
</span><span id="L-5"><a href="#L-5"><span class="linenos">  5</span></a><span class="kn">import</span><span class="w"> </span><span class="nn">glob</span>
</span><span id="L-6"><a href="#L-6"><span class="linenos">  6</span></a><span class="kn">import</span><span class="w"> </span><span class="nn">importlib</span>
</span><span id="L-7"><a href="#L-7"><span class="linenos">  7</span></a><span class="kn">import</span><span class="w"> </span><span class="nn">os</span>
</span><span id="L-8"><a href="#L-8"><span class="linenos">  8</span></a><span class="kn">import</span><span class="w"> </span><span class="nn">re</span>
</span><span id="L-9"><a href="#L-9"><span class="linenos">  9</span></a><span class="kn">import</span><span class="w"> </span><span class="nn">sys</span>
</span><span id="L-10"><a href="#L-10"><span class="linenos"> 10</span></a><span class="kn">from</span><span class="w"> </span><span class="nn">collections</span><span class="w"> </span><span class="kn">import</span> <span class="n">defaultdict</span>
</span><span id="L-11"><a href="#L-11"><span class="linenos"> 11</span></a><span class="kn">from</span><span class="w"> </span><span class="nn">logging</span><span class="w"> </span><span class="kn">import</span> <span class="n">DEBUG</span><span class="p">,</span> <span class="n">INFO</span><span class="p">,</span> <span class="n">basicConfig</span><span class="p">,</span> <span class="n">getLogger</span>
</span><span id="L-12"><a href="#L-12"><span class="linenos"> 12</span></a><span class="kn">from</span><span class="w"> </span><span class="nn">textwrap</span><span class="w"> </span><span class="kn">import</span> <span class="n">fill</span>
</span><span id="L-13"><a href="#L-13"><span class="linenos"> 13</span></a><span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span><span class="p">,</span> <span class="n">Dict</span><span class="p">,</span> <span class="n">List</span><span class="p">,</span> <span class="n">Sequence</span><span class="p">,</span> <span class="n">Tuple</span><span class="p">,</span> <span class="n">Union</span>
</span><span id="L-14"><a href="#L-14"><span class="linenos"> 14</span></a>
</span><span id="L-15"><a href="#L-15"><span class="linenos"> 15</span></a><span class="c1"># import pkg_resources as pr</span>
</span><span id="L-16"><a href="#L-16"><span class="linenos"> 16</span></a>
</span><span id="L-17"><a href="#L-17"><span class="linenos"> 17</span></a><span class="k">if</span> <span class="n">sys</span><span class="o">.</span><span class="n">version_info</span> <span class="o">&lt;</span> <span class="p">(</span><span class="mi">3</span><span class="p">,</span> <span class="mi">10</span><span class="p">):</span>
</span><span id="L-18"><a href="#L-18"><span class="linenos"> 18</span></a>    <span class="kn">from</span><span class="w"> </span><span class="nn">importlib_metadata</span><span class="w"> </span><span class="kn">import</span> <span class="n">entry_points</span>
</span><span id="L-19"><a href="#L-19"><span class="linenos"> 19</span></a><span class="k">else</span><span class="p">:</span>
</span><span id="L-20"><a href="#L-20"><span class="linenos"> 20</span></a>    <span class="kn">from</span><span class="w"> </span><span class="nn">importlib.metadata</span><span class="w"> </span><span class="kn">import</span> <span class="n">entry_points</span>
</span><span id="L-21"><a href="#L-21"><span class="linenos"> 21</span></a>
</span><span id="L-22"><a href="#L-22"><span class="linenos"> 22</span></a>
</span><span id="L-23"><a href="#L-23"><span class="linenos"> 23</span></a><span class="k">def</span><span class="w"> </span><span class="nf">_normalize_unitcell_options</span><span class="p">(</span>
</span><span id="L-24"><a href="#L-24"><span class="linenos"> 24</span></a>    <span class="n">options</span><span class="p">:</span> <span class="n">Sequence</span><span class="p">[</span><span class="n">Union</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">],</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]],</span>
</span><span id="L-25"><a href="#L-25"><span class="linenos"> 25</span></a><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">List</span><span class="p">[</span><span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]:</span>
</span><span id="L-26"><a href="#L-26"><span class="linenos"> 26</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;(name, help) or dict のリストを {name, help, required?, example?} のリストに統一。&quot;&quot;&quot;</span>
</span><span id="L-27"><a href="#L-27"><span class="linenos"> 27</span></a>    <span class="n">result</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="L-28"><a href="#L-28"><span class="linenos"> 28</span></a>    <span class="k">for</span> <span class="n">opt</span> <span class="ow">in</span> <span class="n">options</span><span class="p">:</span>
</span><span id="L-29"><a href="#L-29"><span class="linenos"> 29</span></a>        <span class="k">if</span> <span class="nb">isinstance</span><span class="p">(</span><span class="n">opt</span><span class="p">,</span> <span class="nb">dict</span><span class="p">):</span>
</span><span id="L-30"><a href="#L-30"><span class="linenos"> 30</span></a>            <span class="n">result</span><span class="o">.</span><span class="n">append</span><span class="p">({</span>
</span><span id="L-31"><a href="#L-31"><span class="linenos"> 31</span></a>                <span class="s2">&quot;name&quot;</span><span class="p">:</span> <span class="nb">str</span><span class="p">(</span><span class="n">opt</span><span class="p">[</span><span class="s2">&quot;name&quot;</span><span class="p">]),</span>
</span><span id="L-32"><a href="#L-32"><span class="linenos"> 32</span></a>                <span class="s2">&quot;help&quot;</span><span class="p">:</span> <span class="nb">str</span><span class="p">(</span><span class="n">opt</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;help&quot;</span><span class="p">,</span> <span class="n">opt</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;brief&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">))),</span>
</span><span id="L-33"><a href="#L-33"><span class="linenos"> 33</span></a>                <span class="s2">&quot;required&quot;</span><span class="p">:</span> <span class="nb">bool</span><span class="p">(</span><span class="n">opt</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;required&quot;</span><span class="p">,</span> <span class="kc">False</span><span class="p">)),</span>
</span><span id="L-34"><a href="#L-34"><span class="linenos"> 34</span></a>                <span class="s2">&quot;example&quot;</span><span class="p">:</span> <span class="n">opt</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;example&quot;</span><span class="p">),</span>
</span><span id="L-35"><a href="#L-35"><span class="linenos"> 35</span></a>            <span class="p">})</span>
</span><span id="L-36"><a href="#L-36"><span class="linenos"> 36</span></a>        <span class="k">else</span><span class="p">:</span>
</span><span id="L-37"><a href="#L-37"><span class="linenos"> 37</span></a>            <span class="n">name</span><span class="p">,</span> <span class="n">help_</span> <span class="o">=</span> <span class="n">opt</span><span class="p">[</span><span class="mi">0</span><span class="p">],</span> <span class="n">opt</span><span class="p">[</span><span class="mi">1</span><span class="p">]</span>
</span><span id="L-38"><a href="#L-38"><span class="linenos"> 38</span></a>            <span class="n">required</span> <span class="o">=</span> <span class="n">opt</span><span class="p">[</span><span class="mi">2</span><span class="p">]</span> <span class="k">if</span> <span class="nb">len</span><span class="p">(</span><span class="n">opt</span><span class="p">)</span> <span class="o">&gt;</span> <span class="mi">2</span> <span class="k">else</span> <span class="kc">False</span>
</span><span id="L-39"><a href="#L-39"><span class="linenos"> 39</span></a>            <span class="n">example</span> <span class="o">=</span> <span class="n">opt</span><span class="p">[</span><span class="mi">3</span><span class="p">]</span> <span class="k">if</span> <span class="nb">len</span><span class="p">(</span><span class="n">opt</span><span class="p">)</span> <span class="o">&gt;</span> <span class="mi">3</span> <span class="k">else</span> <span class="kc">None</span>
</span><span id="L-40"><a href="#L-40"><span class="linenos"> 40</span></a>            <span class="n">result</span><span class="o">.</span><span class="n">append</span><span class="p">({</span>
</span><span id="L-41"><a href="#L-41"><span class="linenos"> 41</span></a>                <span class="s2">&quot;name&quot;</span><span class="p">:</span> <span class="nb">str</span><span class="p">(</span><span class="n">name</span><span class="p">),</span>
</span><span id="L-42"><a href="#L-42"><span class="linenos"> 42</span></a>                <span class="s2">&quot;help&quot;</span><span class="p">:</span> <span class="nb">str</span><span class="p">(</span><span class="n">help_</span><span class="p">),</span>
</span><span id="L-43"><a href="#L-43"><span class="linenos"> 43</span></a>                <span class="s2">&quot;required&quot;</span><span class="p">:</span> <span class="nb">bool</span><span class="p">(</span><span class="n">required</span><span class="p">),</span>
</span><span id="L-44"><a href="#L-44"><span class="linenos"> 44</span></a>                <span class="s2">&quot;example&quot;</span><span class="p">:</span> <span class="n">example</span><span class="p">,</span>
</span><span id="L-45"><a href="#L-45"><span class="linenos"> 45</span></a>            <span class="p">})</span>
</span><span id="L-46"><a href="#L-46"><span class="linenos"> 46</span></a>    <span class="k">return</span> <span class="n">result</span>
</span><span id="L-47"><a href="#L-47"><span class="linenos"> 47</span></a>
</span><span id="L-48"><a href="#L-48"><span class="linenos"> 48</span></a>
</span><span id="L-49"><a href="#L-49"><span class="linenos"> 49</span></a><span class="k">def</span><span class="w"> </span><span class="nf">format_unitcell_usage</span><span class="p">(</span>
</span><span id="L-50"><a href="#L-50"><span class="linenos"> 50</span></a>    <span class="n">unitcell_name</span><span class="p">:</span> <span class="nb">str</span><span class="p">,</span> <span class="n">options</span><span class="p">:</span> <span class="n">Sequence</span><span class="p">[</span><span class="n">Union</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">],</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]]</span>
</span><span id="L-51"><a href="#L-51"><span class="linenos"> 51</span></a><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]:</span>
</span><span id="L-52"><a href="#L-52"><span class="linenos"> 52</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-53"><a href="#L-53"><span class="linenos"> 53</span></a><span class="sd">    options 構造体から CLI / API / YAML の 3 表記を生成する。</span>
</span><span id="L-54"><a href="#L-54"><span class="linenos"> 54</span></a><span class="sd">    Returns:</span>
</span><span id="L-55"><a href="#L-55"><span class="linenos"> 55</span></a><span class="sd">        {&quot;cli&quot;: &quot;...&quot;, &quot;api&quot;: &quot;...&quot;, &quot;yaml&quot;: &quot;...&quot;}</span>
</span><span id="L-56"><a href="#L-56"><span class="linenos"> 56</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-57"><a href="#L-57"><span class="linenos"> 57</span></a>    <span class="n">opts</span> <span class="o">=</span> <span class="n">_normalize_unitcell_options</span><span class="p">(</span><span class="n">options</span><span class="p">)</span>
</span><span id="L-58"><a href="#L-58"><span class="linenos"> 58</span></a>    <span class="n">cli_parts</span> <span class="o">=</span> <span class="p">[</span><span class="sa">f</span><span class="s2">&quot;genice3 </span><span class="si">{</span><span class="n">unitcell_name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">]</span>
</span><span id="L-59"><a href="#L-59"><span class="linenos"> 59</span></a>    <span class="n">api_args</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="L-60"><a href="#L-60"><span class="linenos"> 60</span></a>    <span class="n">yaml_lines</span> <span class="o">=</span> <span class="p">[</span><span class="sa">f</span><span class="s2">&quot;unitcell:&quot;</span><span class="p">,</span> <span class="sa">f</span><span class="s2">&quot;  name: </span><span class="si">{</span><span class="n">unitcell_name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">]</span>
</span><span id="L-61"><a href="#L-61"><span class="linenos"> 61</span></a>    <span class="k">for</span> <span class="n">o</span> <span class="ow">in</span> <span class="n">opts</span><span class="p">:</span>
</span><span id="L-62"><a href="#L-62"><span class="linenos"> 62</span></a>        <span class="n">ex</span> <span class="o">=</span> <span class="n">o</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;example&quot;</span><span class="p">)</span>
</span><span id="L-63"><a href="#L-63"><span class="linenos"> 63</span></a>        <span class="n">ex_str</span> <span class="o">=</span> <span class="nb">str</span><span class="p">(</span><span class="n">ex</span><span class="p">)</span> <span class="k">if</span> <span class="n">ex</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span> <span class="k">else</span> <span class="s2">&quot;VALUE&quot;</span>
</span><span id="L-64"><a href="#L-64"><span class="linenos"> 64</span></a>        <span class="n">cli_parts</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;--</span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2"> </span><span class="si">{</span><span class="n">ex_str</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-65"><a href="#L-65"><span class="linenos"> 65</span></a>        <span class="k">if</span> <span class="n">o</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;required&quot;</span><span class="p">):</span>
</span><span id="L-66"><a href="#L-66"><span class="linenos"> 66</span></a>            <span class="n">cli_parts</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="s2">&quot;(required)&quot;</span><span class="p">)</span>
</span><span id="L-67"><a href="#L-67"><span class="linenos"> 67</span></a>        <span class="n">api_args</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">=</span><span class="si">{</span><span class="nb">repr</span><span class="p">(</span><span class="n">ex</span><span class="p">)</span><span class="si">}</span><span class="s2">&quot;</span> <span class="k">if</span> <span class="n">ex</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span> <span class="k">else</span> <span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">=None&quot;</span><span class="p">)</span>
</span><span id="L-68"><a href="#L-68"><span class="linenos"> 68</span></a>        <span class="n">yaml_lines</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;  </span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">: </span><span class="si">{</span><span class="n">ex</span><span class="si">}</span><span class="s2">&quot;</span> <span class="k">if</span> <span class="n">ex</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span> <span class="k">else</span> <span class="sa">f</span><span class="s2">&quot;  </span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">: ...&quot;</span><span class="p">)</span>
</span><span id="L-69"><a href="#L-69"><span class="linenos"> 69</span></a>    <span class="k">return</span> <span class="p">{</span>
</span><span id="L-70"><a href="#L-70"><span class="linenos"> 70</span></a>        <span class="s2">&quot;cli&quot;</span><span class="p">:</span> <span class="s2">&quot; &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">cli_parts</span><span class="p">)</span> <span class="o">+</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">  &quot;</span> <span class="o">+</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">  &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;--</span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">: </span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;help&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">&quot;</span> <span class="k">for</span> <span class="n">o</span> <span class="ow">in</span> <span class="n">opts</span><span class="p">),</span>
</span><span id="L-71"><a href="#L-71"><span class="linenos"> 71</span></a>        <span class="s2">&quot;api&quot;</span><span class="p">:</span> <span class="sa">f</span><span class="s1">&#39;UnitCell(&quot;</span><span class="si">{</span><span class="n">unitcell_name</span><span class="si">}</span><span class="s1">&quot;, &#39;</span> <span class="o">+</span> <span class="s2">&quot;, &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">api_args</span><span class="p">)</span> <span class="o">+</span> <span class="s2">&quot;)&quot;</span><span class="p">,</span>
</span><span id="L-72"><a href="#L-72"><span class="linenos"> 72</span></a>        <span class="s2">&quot;yaml&quot;</span><span class="p">:</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">&quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">yaml_lines</span><span class="p">),</span>
</span><span id="L-73"><a href="#L-73"><span class="linenos"> 73</span></a>    <span class="p">}</span>
</span><span id="L-74"><a href="#L-74"><span class="linenos"> 74</span></a>
</span><span id="L-75"><a href="#L-75"><span class="linenos"> 75</span></a>
</span><span id="L-76"><a href="#L-76"><span class="linenos"> 76</span></a><span class="k">def</span><span class="w"> </span><span class="nf">_is_water_module</span><span class="p">(</span><span class="n">module</span><span class="p">,</span> <span class="n">category</span><span class="p">):</span>
</span><span id="L-77"><a href="#L-77"><span class="linenos"> 77</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;Return True if the module is a water model (for molecule plugins).&quot;&quot;&quot;</span>
</span><span id="L-78"><a href="#L-78"><span class="linenos"> 78</span></a>    <span class="k">if</span> <span class="n">category</span> <span class="o">!=</span> <span class="s2">&quot;molecule&quot;</span><span class="p">:</span>
</span><span id="L-79"><a href="#L-79"><span class="linenos"> 79</span></a>        <span class="k">return</span> <span class="kc">False</span>
</span><span id="L-80"><a href="#L-80"><span class="linenos"> 80</span></a>    <span class="k">if</span> <span class="s2">&quot;water&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="L-81"><a href="#L-81"><span class="linenos"> 81</span></a>        <span class="k">return</span> <span class="kc">True</span>
</span><span id="L-82"><a href="#L-82"><span class="linenos"> 82</span></a>    <span class="k">if</span> <span class="nb">hasattr</span><span class="p">(</span><span class="n">module</span><span class="p">,</span> <span class="s2">&quot;Molecule&quot;</span><span class="p">):</span>
</span><span id="L-83"><a href="#L-83"><span class="linenos"> 83</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="L-84"><a href="#L-84"><span class="linenos"> 84</span></a>            <span class="n">m</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">Molecule</span><span class="p">()</span>
</span><span id="L-85"><a href="#L-85"><span class="linenos"> 85</span></a>            <span class="k">return</span> <span class="nb">getattr</span><span class="p">(</span><span class="n">m</span><span class="p">,</span> <span class="s2">&quot;is_water&quot;</span><span class="p">,</span> <span class="kc">False</span><span class="p">)</span>
</span><span id="L-86"><a href="#L-86"><span class="linenos"> 86</span></a>        <span class="k">except</span> <span class="ne">Exception</span><span class="p">:</span>
</span><span id="L-87"><a href="#L-87"><span class="linenos"> 87</span></a>            <span class="k">pass</span>
</span><span id="L-88"><a href="#L-88"><span class="linenos"> 88</span></a>    <span class="k">return</span> <span class="kc">False</span>
</span><span id="L-89"><a href="#L-89"><span class="linenos"> 89</span></a>
</span><span id="L-90"><a href="#L-90"><span class="linenos"> 90</span></a>
</span><span id="L-91"><a href="#L-91"><span class="linenos"> 91</span></a><span class="k">def</span><span class="w"> </span><span class="nf">scan</span><span class="p">(</span><span class="n">category</span><span class="p">):</span>
</span><span id="L-92"><a href="#L-92"><span class="linenos"> 92</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-93"><a href="#L-93"><span class="linenos"> 93</span></a><span class="sd">    Scan available plugins.</span>
</span><span id="L-94"><a href="#L-94"><span class="linenos"> 94</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-95"><a href="#L-95"><span class="linenos"> 95</span></a>    <span class="n">logger</span> <span class="o">=</span> <span class="n">getLogger</span><span class="p">()</span>
</span><span id="L-96"><a href="#L-96"><span class="linenos"> 96</span></a>
</span><span id="L-97"><a href="#L-97"><span class="linenos"> 97</span></a>    <span class="n">modules</span> <span class="o">=</span> <span class="p">{}</span>
</span><span id="L-98"><a href="#L-98"><span class="linenos"> 98</span></a>    <span class="n">desc</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="L-99"><a href="#L-99"><span class="linenos"> 99</span></a>    <span class="n">iswater</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="L-100"><a href="#L-100"><span class="linenos">100</span></a>    <span class="n">refs</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="L-101"><a href="#L-101"><span class="linenos">101</span></a>    <span class="n">tests</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="L-102"><a href="#L-102"><span class="linenos">102</span></a>
</span><span id="L-103"><a href="#L-103"><span class="linenos">103</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="se">\n</span><span class="s2">Predefined </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-104"><a href="#L-104"><span class="linenos">104</span></a>    <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;genice3.</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-105"><a href="#L-105"><span class="linenos">105</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="L-106"><a href="#L-106"><span class="linenos">106</span></a>    <span class="k">for</span> <span class="n">path</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">__path__</span><span class="p">:</span>
</span><span id="L-107"><a href="#L-107"><span class="linenos">107</span></a>        <span class="k">for</span> <span class="n">mod</span> <span class="ow">in</span> <span class="nb">sorted</span><span class="p">(</span><span class="n">glob</span><span class="o">.</span><span class="n">glob</span><span class="p">(</span><span class="n">path</span> <span class="o">+</span> <span class="s2">&quot;/*.py&quot;</span><span class="p">)):</span>
</span><span id="L-108"><a href="#L-108"><span class="linenos">108</span></a>            <span class="n">mod</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">basename</span><span class="p">(</span><span class="n">mod</span><span class="p">)[:</span><span class="o">-</span><span class="mi">3</span><span class="p">]</span>
</span><span id="L-109"><a href="#L-109"><span class="linenos">109</span></a>            <span class="k">if</span> <span class="n">mod</span><span class="p">[:</span><span class="mi">2</span><span class="p">]</span> <span class="o">!=</span> <span class="s2">&quot;__&quot;</span><span class="p">:</span>
</span><span id="L-110"><a href="#L-110"><span class="linenos">110</span></a>                <span class="n">mods</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">mod</span><span class="p">)</span>
</span><span id="L-111"><a href="#L-111"><span class="linenos">111</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="n">mods</span><span class="p">)</span>
</span><span id="L-112"><a href="#L-112"><span class="linenos">112</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;system&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">mods</span>
</span><span id="L-113"><a href="#L-113"><span class="linenos">113</span></a>
</span><span id="L-114"><a href="#L-114"><span class="linenos">114</span></a>    <span class="k">for</span> <span class="n">mod</span> <span class="ow">in</span> <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;system&quot;</span><span class="p">]:</span>
</span><span id="L-115"><a href="#L-115"><span class="linenos">115</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="L-116"><a href="#L-116"><span class="linenos">116</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;genice3.</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">mod</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-117"><a href="#L-117"><span class="linenos">117</span></a>            <span class="k">if</span> <span class="s2">&quot;desc&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="L-118"><a href="#L-118"><span class="linenos">118</span></a>                <span class="n">desc</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;brief&quot;</span><span class="p">]</span>
</span><span id="L-119"><a href="#L-119"><span class="linenos">119</span></a>                <span class="k">if</span> <span class="s2">&quot;ref&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="L-120"><a href="#L-120"><span class="linenos">120</span></a>                    <span class="n">refs</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;ref&quot;</span><span class="p">]</span>
</span><span id="L-121"><a href="#L-121"><span class="linenos">121</span></a>                <span class="k">if</span> <span class="s2">&quot;test&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="L-122"><a href="#L-122"><span class="linenos">122</span></a>                    <span class="n">tests</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;test&quot;</span><span class="p">]</span>
</span><span id="L-123"><a href="#L-123"><span class="linenos">123</span></a>            <span class="n">iswater</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">_is_water_module</span><span class="p">(</span><span class="n">module</span><span class="p">,</span> <span class="n">category</span><span class="p">)</span>
</span><span id="L-124"><a href="#L-124"><span class="linenos">124</span></a>        <span class="k">except</span> <span class="ne">BaseException</span><span class="p">:</span>
</span><span id="L-125"><a href="#L-125"><span class="linenos">125</span></a>            <span class="k">pass</span>
</span><span id="L-126"><a href="#L-126"><span class="linenos">126</span></a>
</span><span id="L-127"><a href="#L-127"><span class="linenos">127</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Extra </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-128"><a href="#L-128"><span class="linenos">128</span></a>    <span class="n">groupname</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot;genice3_</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="L-129"><a href="#L-129"><span class="linenos">129</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="L-130"><a href="#L-130"><span class="linenos">130</span></a>    <span class="c1"># for ep in pr.iter_entry_points(group=groupname):</span>
</span><span id="L-131"><a href="#L-131"><span class="linenos">131</span></a>    <span class="k">for</span> <span class="n">ep</span> <span class="ow">in</span> <span class="n">entry_points</span><span class="p">(</span><span class="n">group</span><span class="o">=</span><span class="n">groupname</span><span class="p">):</span>
</span><span id="L-132"><a href="#L-132"><span class="linenos">132</span></a>        <span class="n">mods</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">ep</span><span class="o">.</span><span class="n">name</span><span class="p">)</span>
</span><span id="L-133"><a href="#L-133"><span class="linenos">133</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="L-134"><a href="#L-134"><span class="linenos">134</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">ep</span><span class="o">.</span><span class="n">load</span><span class="p">()</span>
</span><span id="L-135"><a href="#L-135"><span class="linenos">135</span></a>            <span class="k">if</span> <span class="s2">&quot;desc&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="L-136"><a href="#L-136"><span class="linenos">136</span></a>                <span class="n">desc</span><span class="p">[</span><span class="n">ep</span><span class="o">.</span><span class="n">name</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;brief&quot;</span><span class="p">]</span>
</span><span id="L-137"><a href="#L-137"><span class="linenos">137</span></a>                <span class="k">if</span> <span class="s2">&quot;ref&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="L-138"><a href="#L-138"><span class="linenos">138</span></a>                    <span class="n">refs</span><span class="p">[</span><span class="n">ep</span><span class="o">.</span><span class="n">name</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;ref&quot;</span><span class="p">]</span>
</span><span id="L-139"><a href="#L-139"><span class="linenos">139</span></a>                <span class="k">if</span> <span class="s2">&quot;test&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="L-140"><a href="#L-140"><span class="linenos">140</span></a>                    <span class="n">tests</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;test&quot;</span><span class="p">]</span>
</span><span id="L-141"><a href="#L-141"><span class="linenos">141</span></a>            <span class="n">iswater</span><span class="p">[</span><span class="n">ep</span><span class="o">.</span><span class="n">name</span><span class="p">]</span> <span class="o">=</span> <span class="n">_is_water_module</span><span class="p">(</span><span class="n">module</span><span class="p">,</span> <span class="n">category</span><span class="p">)</span>
</span><span id="L-142"><a href="#L-142"><span class="linenos">142</span></a>        <span class="k">except</span> <span class="ne">BaseException</span><span class="p">:</span>
</span><span id="L-143"><a href="#L-143"><span class="linenos">143</span></a>            <span class="k">pass</span>
</span><span id="L-144"><a href="#L-144"><span class="linenos">144</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="n">mods</span><span class="p">)</span>
</span><span id="L-145"><a href="#L-145"><span class="linenos">145</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;extra&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">mods</span>
</span><span id="L-146"><a href="#L-146"><span class="linenos">146</span></a>
</span><span id="L-147"><a href="#L-147"><span class="linenos">147</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Local </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-148"><a href="#L-148"><span class="linenos">148</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="p">[</span>
</span><span id="L-149"><a href="#L-149"><span class="linenos">149</span></a>        <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">basename</span><span class="p">(</span><span class="n">mod</span><span class="p">)[:</span><span class="o">-</span><span class="mi">3</span><span class="p">]</span> <span class="k">for</span> <span class="n">mod</span> <span class="ow">in</span> <span class="nb">sorted</span><span class="p">(</span><span class="n">glob</span><span class="o">.</span><span class="n">glob</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;./</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">/*.py&quot;</span><span class="p">))</span>
</span><span id="L-150"><a href="#L-150"><span class="linenos">150</span></a>    <span class="p">]</span>
</span><span id="L-151"><a href="#L-151"><span class="linenos">151</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="n">mods</span><span class="p">)</span>
</span><span id="L-152"><a href="#L-152"><span class="linenos">152</span></a>    <span class="k">for</span> <span class="n">mod</span> <span class="ow">in</span> <span class="n">mods</span><span class="p">:</span>
</span><span id="L-153"><a href="#L-153"><span class="linenos">153</span></a>        <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">mod</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-154"><a href="#L-154"><span class="linenos">154</span></a>        <span class="k">if</span> <span class="s2">&quot;desc&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="L-155"><a href="#L-155"><span class="linenos">155</span></a>            <span class="n">desc</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;brief&quot;</span><span class="p">]</span>
</span><span id="L-156"><a href="#L-156"><span class="linenos">156</span></a>            <span class="k">if</span> <span class="s2">&quot;ref&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="L-157"><a href="#L-157"><span class="linenos">157</span></a>                <span class="n">refs</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;ref&quot;</span><span class="p">]</span>
</span><span id="L-158"><a href="#L-158"><span class="linenos">158</span></a>            <span class="k">if</span> <span class="s2">&quot;test&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="L-159"><a href="#L-159"><span class="linenos">159</span></a>                <span class="n">tests</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;test&quot;</span><span class="p">]</span>
</span><span id="L-160"><a href="#L-160"><span class="linenos">160</span></a>        <span class="n">iswater</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">_is_water_module</span><span class="p">(</span><span class="n">module</span><span class="p">,</span> <span class="n">category</span><span class="p">)</span>
</span><span id="L-161"><a href="#L-161"><span class="linenos">161</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="n">mods</span><span class="p">)</span>
</span><span id="L-162"><a href="#L-162"><span class="linenos">162</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;local&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">mods</span>
</span><span id="L-163"><a href="#L-163"><span class="linenos">163</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;desc&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">desc</span>
</span><span id="L-164"><a href="#L-164"><span class="linenos">164</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;iswater&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">iswater</span>
</span><span id="L-165"><a href="#L-165"><span class="linenos">165</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;refs&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">refs</span>
</span><span id="L-166"><a href="#L-166"><span class="linenos">166</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;tests&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">tests</span>
</span><span id="L-167"><a href="#L-167"><span class="linenos">167</span></a>
</span><span id="L-168"><a href="#L-168"><span class="linenos">168</span></a>    <span class="k">return</span> <span class="n">modules</span>
</span><span id="L-169"><a href="#L-169"><span class="linenos">169</span></a>
</span><span id="L-170"><a href="#L-170"><span class="linenos">170</span></a>
</span><span id="L-171"><a href="#L-171"><span class="linenos">171</span></a><span class="k">def</span><span class="w"> </span><span class="nf">descriptions</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">width</span><span class="o">=</span><span class="mi">72</span><span class="p">,</span> <span class="n">water</span><span class="o">=</span><span class="kc">False</span><span class="p">,</span> <span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s2">&quot;system&quot;</span><span class="p">,</span> <span class="s2">&quot;extra&quot;</span><span class="p">,</span> <span class="s2">&quot;local&quot;</span><span class="p">)):</span>
</span><span id="L-172"><a href="#L-172"><span class="linenos">172</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-173"><a href="#L-173"><span class="linenos">173</span></a><span class="sd">    Show the list of available plugins in the category.</span>
</span><span id="L-174"><a href="#L-174"><span class="linenos">174</span></a>
</span><span id="L-175"><a href="#L-175"><span class="linenos">175</span></a><span class="sd">    Options:</span>
</span><span id="L-176"><a href="#L-176"><span class="linenos">176</span></a><span class="sd">      width=72      Width of the output.</span>
</span><span id="L-177"><a href="#L-177"><span class="linenos">177</span></a><span class="sd">      water=False   Pick up water molecules only (for molecule plugin).</span>
</span><span id="L-178"><a href="#L-178"><span class="linenos">178</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-179"><a href="#L-179"><span class="linenos">179</span></a>    <span class="n">titles</span> <span class="o">=</span> <span class="p">{</span>
</span><span id="L-180"><a href="#L-180"><span class="linenos">180</span></a>        <span class="s2">&quot;lattice&quot;</span><span class="p">:</span> <span class="p">{</span>
</span><span id="L-181"><a href="#L-181"><span class="linenos">181</span></a>            <span class="s2">&quot;system&quot;</span><span class="p">:</span> <span class="s2">&quot;1. Lattice structures served with GenIce&quot;</span><span class="p">,</span>
</span><span id="L-182"><a href="#L-182"><span class="linenos">182</span></a>            <span class="s2">&quot;extra&quot;</span><span class="p">:</span> <span class="s2">&quot;2. Lattice structures served by external plugins&quot;</span><span class="p">,</span>
</span><span id="L-183"><a href="#L-183"><span class="linenos">183</span></a>            <span class="s2">&quot;local&quot;</span><span class="p">:</span> <span class="s2">&quot;3. Lattice structures served locally&quot;</span><span class="p">,</span>
</span><span id="L-184"><a href="#L-184"><span class="linenos">184</span></a>            <span class="s2">&quot;title&quot;</span><span class="p">:</span> <span class="s2">&quot;[Available lattice structures]&quot;</span><span class="p">,</span>
</span><span id="L-185"><a href="#L-185"><span class="linenos">185</span></a>        <span class="p">},</span>
</span><span id="L-186"><a href="#L-186"><span class="linenos">186</span></a>        <span class="s2">&quot;format&quot;</span><span class="p">:</span> <span class="p">{</span>
</span><span id="L-187"><a href="#L-187"><span class="linenos">187</span></a>            <span class="s2">&quot;system&quot;</span><span class="p">:</span> <span class="s2">&quot;1. Formatters served with GenIce&quot;</span><span class="p">,</span>
</span><span id="L-188"><a href="#L-188"><span class="linenos">188</span></a>            <span class="s2">&quot;extra&quot;</span><span class="p">:</span> <span class="s2">&quot;2. Formatters served by external plugins&quot;</span><span class="p">,</span>
</span><span id="L-189"><a href="#L-189"><span class="linenos">189</span></a>            <span class="s2">&quot;local&quot;</span><span class="p">:</span> <span class="s2">&quot;3. Formatters served locally&quot;</span><span class="p">,</span>
</span><span id="L-190"><a href="#L-190"><span class="linenos">190</span></a>            <span class="s2">&quot;title&quot;</span><span class="p">:</span> <span class="s2">&quot;[Available formatters]&quot;</span><span class="p">,</span>
</span><span id="L-191"><a href="#L-191"><span class="linenos">191</span></a>        <span class="p">},</span>
</span><span id="L-192"><a href="#L-192"><span class="linenos">192</span></a>        <span class="s2">&quot;loader&quot;</span><span class="p">:</span> <span class="p">{</span>
</span><span id="L-193"><a href="#L-193"><span class="linenos">193</span></a>            <span class="s2">&quot;system&quot;</span><span class="p">:</span> <span class="s2">&quot;1. File types served with GenIce&quot;</span><span class="p">,</span>
</span><span id="L-194"><a href="#L-194"><span class="linenos">194</span></a>            <span class="s2">&quot;extra&quot;</span><span class="p">:</span> <span class="s2">&quot;2. File types served by external eplugins&quot;</span><span class="p">,</span>
</span><span id="L-195"><a href="#L-195"><span class="linenos">195</span></a>            <span class="s2">&quot;local&quot;</span><span class="p">:</span> <span class="s2">&quot;3. File types served locally&quot;</span><span class="p">,</span>
</span><span id="L-196"><a href="#L-196"><span class="linenos">196</span></a>            <span class="s2">&quot;title&quot;</span><span class="p">:</span> <span class="s2">&quot;[Available input file types]&quot;</span><span class="p">,</span>
</span><span id="L-197"><a href="#L-197"><span class="linenos">197</span></a>        <span class="p">},</span>
</span><span id="L-198"><a href="#L-198"><span class="linenos">198</span></a>        <span class="s2">&quot;molecule&quot;</span><span class="p">:</span> <span class="p">{</span>
</span><span id="L-199"><a href="#L-199"><span class="linenos">199</span></a>            <span class="s2">&quot;system&quot;</span><span class="p">:</span> <span class="s2">&quot;1. Molecules served with GenIce&quot;</span><span class="p">,</span>
</span><span id="L-200"><a href="#L-200"><span class="linenos">200</span></a>            <span class="s2">&quot;extra&quot;</span><span class="p">:</span> <span class="s2">&quot;2. Molecules served by external plugins&quot;</span><span class="p">,</span>
</span><span id="L-201"><a href="#L-201"><span class="linenos">201</span></a>            <span class="s2">&quot;local&quot;</span><span class="p">:</span> <span class="s2">&quot;3. Molecules served locally&quot;</span><span class="p">,</span>
</span><span id="L-202"><a href="#L-202"><span class="linenos">202</span></a>            <span class="s2">&quot;title&quot;</span><span class="p">:</span> <span class="s2">&quot;[Available molecules]&quot;</span><span class="p">,</span>
</span><span id="L-203"><a href="#L-203"><span class="linenos">203</span></a>        <span class="p">},</span>
</span><span id="L-204"><a href="#L-204"><span class="linenos">204</span></a>    <span class="p">}</span>
</span><span id="L-205"><a href="#L-205"><span class="linenos">205</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="n">scan</span><span class="p">(</span><span class="n">category</span><span class="p">)</span>
</span><span id="L-206"><a href="#L-206"><span class="linenos">206</span></a>    <span class="n">catalog</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot; </span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="si">{</span><span class="n">titles</span><span class="p">[</span><span class="n">category</span><span class="p">][</span><span class="s1">&#39;title&#39;</span><span class="p">]</span><span class="si">}</span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="L-207"><a href="#L-207"><span class="linenos">207</span></a>    <span class="n">desc</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;desc&quot;</span><span class="p">]</span>
</span><span id="L-208"><a href="#L-208"><span class="linenos">208</span></a>    <span class="n">iswater</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;iswater&quot;</span><span class="p">]</span>
</span><span id="L-209"><a href="#L-209"><span class="linenos">209</span></a>    <span class="k">for</span> <span class="n">group</span> <span class="ow">in</span> <span class="n">groups</span><span class="p">:</span>
</span><span id="L-210"><a href="#L-210"><span class="linenos">210</span></a>        <span class="n">desced</span> <span class="o">=</span> <span class="n">defaultdict</span><span class="p">(</span><span class="nb">list</span><span class="p">)</span>
</span><span id="L-211"><a href="#L-211"><span class="linenos">211</span></a>        <span class="n">undesc</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="L-212"><a href="#L-212"><span class="linenos">212</span></a>        <span class="k">for</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">mods</span><span class="p">[</span><span class="n">group</span><span class="p">]:</span>
</span><span id="L-213"><a href="#L-213"><span class="linenos">213</span></a>            <span class="k">if</span> <span class="n">category</span> <span class="o">==</span> <span class="s2">&quot;molecule&quot;</span><span class="p">:</span>
</span><span id="L-214"><a href="#L-214"><span class="linenos">214</span></a>                <span class="k">if</span> <span class="n">L</span> <span class="ow">not</span> <span class="ow">in</span> <span class="n">iswater</span><span class="p">:</span>
</span><span id="L-215"><a href="#L-215"><span class="linenos">215</span></a>                    <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]</span> <span class="o">=</span> <span class="kc">False</span>
</span><span id="L-216"><a href="#L-216"><span class="linenos">216</span></a>                <span class="k">if</span> <span class="n">water</span> <span class="ow">and</span> <span class="ow">not</span> <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]:</span>
</span><span id="L-217"><a href="#L-217"><span class="linenos">217</span></a>                    <span class="k">continue</span>
</span><span id="L-218"><a href="#L-218"><span class="linenos">218</span></a>                <span class="k">if</span> <span class="ow">not</span> <span class="n">water</span> <span class="ow">and</span> <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]:</span>
</span><span id="L-219"><a href="#L-219"><span class="linenos">219</span></a>                    <span class="k">continue</span>
</span><span id="L-220"><a href="#L-220"><span class="linenos">220</span></a>            <span class="k">if</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">desc</span><span class="p">:</span>
</span><span id="L-221"><a href="#L-221"><span class="linenos">221</span></a>                <span class="n">desced</span><span class="p">[</span><span class="n">desc</span><span class="p">[</span><span class="n">L</span><span class="p">]]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">L</span><span class="p">)</span>
</span><span id="L-222"><a href="#L-222"><span class="linenos">222</span></a>            <span class="k">else</span><span class="p">:</span>
</span><span id="L-223"><a href="#L-223"><span class="linenos">223</span></a>                <span class="n">undesc</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">L</span><span class="p">)</span>
</span><span id="L-224"><a href="#L-224"><span class="linenos">224</span></a>        <span class="k">for</span> <span class="n">dd</span> <span class="ow">in</span> <span class="n">desced</span><span class="p">:</span>
</span><span id="L-225"><a href="#L-225"><span class="linenos">225</span></a>            <span class="n">desced</span><span class="p">[</span><span class="n">dd</span><span class="p">]</span> <span class="o">=</span> <span class="s2">&quot;, &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">desced</span><span class="p">[</span><span class="n">dd</span><span class="p">])</span>
</span><span id="L-226"><a href="#L-226"><span class="linenos">226</span></a>        <span class="n">catalog</span> <span class="o">+=</span> <span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">titles</span><span class="p">[</span><span class="n">category</span><span class="p">][</span><span class="n">group</span><span class="p">]</span><span class="si">}</span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="L-227"><a href="#L-227"><span class="linenos">227</span></a>        <span class="n">table</span> <span class="o">=</span> <span class="s2">&quot;&quot;</span>
</span><span id="L-228"><a href="#L-228"><span class="linenos">228</span></a>        <span class="k">for</span> <span class="n">dd</span> <span class="ow">in</span> <span class="nb">sorted</span><span class="p">(</span><span class="n">desced</span><span class="p">,</span> <span class="n">key</span><span class="o">=</span><span class="k">lambda</span> <span class="n">x</span><span class="p">:</span> <span class="n">desced</span><span class="p">[</span><span class="n">x</span><span class="p">]):</span>
</span><span id="L-229"><a href="#L-229"><span class="linenos">229</span></a>            <span class="n">table</span> <span class="o">+=</span> <span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">desced</span><span class="p">[</span><span class="n">dd</span><span class="p">]</span><span class="si">}</span><span class="se">\t</span><span class="si">{</span><span class="n">dd</span><span class="si">}</span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="L-230"><a href="#L-230"><span class="linenos">230</span></a>        <span class="k">if</span> <span class="n">table</span> <span class="o">==</span> <span class="s2">&quot;&quot;</span><span class="p">:</span>
</span><span id="L-231"><a href="#L-231"><span class="linenos">231</span></a>            <span class="n">table</span> <span class="o">=</span> <span class="s2">&quot;(None)</span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="L-232"><a href="#L-232"><span class="linenos">232</span></a>        <span class="n">table</span> <span class="o">=</span> <span class="p">[</span>
</span><span id="L-233"><a href="#L-233"><span class="linenos">233</span></a>            <span class="n">fill</span><span class="p">(</span>
</span><span id="L-234"><a href="#L-234"><span class="linenos">234</span></a>                <span class="n">line</span><span class="p">,</span>
</span><span id="L-235"><a href="#L-235"><span class="linenos">235</span></a>                <span class="n">width</span><span class="o">=</span><span class="n">width</span><span class="p">,</span>
</span><span id="L-236"><a href="#L-236"><span class="linenos">236</span></a>                <span class="n">drop_whitespace</span><span class="o">=</span><span class="kc">False</span><span class="p">,</span>
</span><span id="L-237"><a href="#L-237"><span class="linenos">237</span></a>                <span class="n">expand_tabs</span><span class="o">=</span><span class="kc">True</span><span class="p">,</span>
</span><span id="L-238"><a href="#L-238"><span class="linenos">238</span></a>                <span class="n">tabsize</span><span class="o">=</span><span class="mi">16</span><span class="p">,</span>
</span><span id="L-239"><a href="#L-239"><span class="linenos">239</span></a>                <span class="n">subsequent_indent</span><span class="o">=</span><span class="s2">&quot; &quot;</span> <span class="o">*</span> <span class="mi">16</span><span class="p">,</span>
</span><span id="L-240"><a href="#L-240"><span class="linenos">240</span></a>            <span class="p">)</span>
</span><span id="L-241"><a href="#L-241"><span class="linenos">241</span></a>            <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">table</span><span class="o">.</span><span class="n">splitlines</span><span class="p">()</span>
</span><span id="L-242"><a href="#L-242"><span class="linenos">242</span></a>        <span class="p">]</span>
</span><span id="L-243"><a href="#L-243"><span class="linenos">243</span></a>        <span class="n">table</span> <span class="o">=</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">&quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">table</span><span class="p">)</span> <span class="o">+</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="L-244"><a href="#L-244"><span class="linenos">244</span></a>        <span class="n">undesc</span> <span class="o">=</span> <span class="s2">&quot; &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">undesc</span><span class="p">)</span>
</span><span id="L-245"><a href="#L-245"><span class="linenos">245</span></a>        <span class="k">if</span> <span class="n">undesc</span> <span class="o">!=</span> <span class="s2">&quot;&quot;</span><span class="p">:</span>
</span><span id="L-246"><a href="#L-246"><span class="linenos">246</span></a>            <span class="n">undesc</span> <span class="o">=</span> <span class="s2">&quot;(Undocumented) &quot;</span> <span class="o">+</span> <span class="n">undesc</span>
</span><span id="L-247"><a href="#L-247"><span class="linenos">247</span></a>        <span class="n">catalog</span> <span class="o">+=</span> <span class="n">table</span> <span class="o">+</span> <span class="s2">&quot;----</span><span class="se">\n</span><span class="s2">&quot;</span> <span class="o">+</span> <span class="n">undesc</span> <span class="o">+</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="L-248"><a href="#L-248"><span class="linenos">248</span></a>    <span class="k">return</span> <span class="n">catalog</span>
</span><span id="L-249"><a href="#L-249"><span class="linenos">249</span></a>
</span><span id="L-250"><a href="#L-250"><span class="linenos">250</span></a>
</span><span id="L-251"><a href="#L-251"><span class="linenos">251</span></a><span class="k">def</span><span class="w"> </span><span class="nf">plugin_descriptors</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">water</span><span class="o">=</span><span class="kc">False</span><span class="p">,</span> <span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s2">&quot;system&quot;</span><span class="p">,</span> <span class="s2">&quot;extra&quot;</span><span class="p">,</span> <span class="s2">&quot;local&quot;</span><span class="p">)):</span>
</span><span id="L-252"><a href="#L-252"><span class="linenos">252</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-253"><a href="#L-253"><span class="linenos">253</span></a><span class="sd">    Show the list of available plugins in the category.</span>
</span><span id="L-254"><a href="#L-254"><span class="linenos">254</span></a>
</span><span id="L-255"><a href="#L-255"><span class="linenos">255</span></a><span class="sd">    Options:</span>
</span><span id="L-256"><a href="#L-256"><span class="linenos">256</span></a><span class="sd">      water=False   Pick up water molecules only (for molecule plugin).</span>
</span><span id="L-257"><a href="#L-257"><span class="linenos">257</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-258"><a href="#L-258"><span class="linenos">258</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="n">scan</span><span class="p">(</span><span class="n">category</span><span class="p">)</span>
</span><span id="L-259"><a href="#L-259"><span class="linenos">259</span></a>    <span class="n">catalog</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="L-260"><a href="#L-260"><span class="linenos">260</span></a>    <span class="n">desc</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;desc&quot;</span><span class="p">]</span>
</span><span id="L-261"><a href="#L-261"><span class="linenos">261</span></a>    <span class="n">iswater</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;iswater&quot;</span><span class="p">]</span>
</span><span id="L-262"><a href="#L-262"><span class="linenos">262</span></a>    <span class="n">refs</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;refs&quot;</span><span class="p">]</span>
</span><span id="L-263"><a href="#L-263"><span class="linenos">263</span></a>    <span class="k">for</span> <span class="n">group</span> <span class="ow">in</span> <span class="n">groups</span><span class="p">:</span>
</span><span id="L-264"><a href="#L-264"><span class="linenos">264</span></a>        <span class="n">desced</span> <span class="o">=</span> <span class="n">defaultdict</span><span class="p">(</span><span class="nb">list</span><span class="p">)</span>
</span><span id="L-265"><a href="#L-265"><span class="linenos">265</span></a>        <span class="n">undesc</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="L-266"><a href="#L-266"><span class="linenos">266</span></a>        <span class="n">refss</span> <span class="o">=</span> <span class="n">defaultdict</span><span class="p">(</span><span class="nb">set</span><span class="p">)</span>
</span><span id="L-267"><a href="#L-267"><span class="linenos">267</span></a>        <span class="k">for</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">mods</span><span class="p">[</span><span class="n">group</span><span class="p">]:</span>
</span><span id="L-268"><a href="#L-268"><span class="linenos">268</span></a>            <span class="k">if</span> <span class="n">category</span> <span class="o">==</span> <span class="s2">&quot;molecule&quot;</span><span class="p">:</span>
</span><span id="L-269"><a href="#L-269"><span class="linenos">269</span></a>                <span class="k">if</span> <span class="n">L</span> <span class="ow">not</span> <span class="ow">in</span> <span class="n">iswater</span><span class="p">:</span>
</span><span id="L-270"><a href="#L-270"><span class="linenos">270</span></a>                    <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]</span> <span class="o">=</span> <span class="kc">False</span>
</span><span id="L-271"><a href="#L-271"><span class="linenos">271</span></a>                <span class="k">if</span> <span class="n">water</span> <span class="ow">and</span> <span class="ow">not</span> <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]:</span>
</span><span id="L-272"><a href="#L-272"><span class="linenos">272</span></a>                    <span class="k">continue</span>
</span><span id="L-273"><a href="#L-273"><span class="linenos">273</span></a>                <span class="k">if</span> <span class="ow">not</span> <span class="n">water</span> <span class="ow">and</span> <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]:</span>
</span><span id="L-274"><a href="#L-274"><span class="linenos">274</span></a>                    <span class="k">continue</span>
</span><span id="L-275"><a href="#L-275"><span class="linenos">275</span></a>            <span class="k">if</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">desc</span><span class="p">:</span>
</span><span id="L-276"><a href="#L-276"><span class="linenos">276</span></a>                <span class="c1"># desc[L] is the brief description of the module</span>
</span><span id="L-277"><a href="#L-277"><span class="linenos">277</span></a>                <span class="c1"># L is the name of module (name of ice)</span>
</span><span id="L-278"><a href="#L-278"><span class="linenos">278</span></a>                <span class="n">desced</span><span class="p">[</span><span class="n">desc</span><span class="p">[</span><span class="n">L</span><span class="p">]]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">L</span><span class="p">)</span>
</span><span id="L-279"><a href="#L-279"><span class="linenos">279</span></a>                <span class="k">if</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">refs</span><span class="p">:</span>
</span><span id="L-280"><a href="#L-280"><span class="linenos">280</span></a>                    <span class="n">refss</span><span class="p">[</span><span class="n">desc</span><span class="p">[</span><span class="n">L</span><span class="p">]]</span> <span class="o">|=</span> <span class="nb">set</span><span class="p">([</span><span class="n">label</span> <span class="k">for</span> <span class="n">key</span><span class="p">,</span> <span class="n">label</span> <span class="ow">in</span> <span class="n">refs</span><span class="p">[</span><span class="n">L</span><span class="p">]</span><span class="o">.</span><span class="n">items</span><span class="p">()])</span>
</span><span id="L-281"><a href="#L-281"><span class="linenos">281</span></a>            <span class="k">else</span><span class="p">:</span>
</span><span id="L-282"><a href="#L-282"><span class="linenos">282</span></a>                <span class="n">undesc</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">L</span><span class="p">)</span>
</span><span id="L-283"><a href="#L-283"><span class="linenos">283</span></a>        <span class="n">catalog</span><span class="p">[</span><span class="n">group</span><span class="p">]</span> <span class="o">=</span> <span class="p">[</span><span class="n">desced</span><span class="p">,</span> <span class="n">undesc</span><span class="p">,</span> <span class="n">refss</span><span class="p">]</span>
</span><span id="L-284"><a href="#L-284"><span class="linenos">284</span></a>    <span class="k">return</span> <span class="n">catalog</span>
</span><span id="L-285"><a href="#L-285"><span class="linenos">285</span></a>
</span><span id="L-286"><a href="#L-286"><span class="linenos">286</span></a>
</span><span id="L-287"><a href="#L-287"><span class="linenos">287</span></a><span class="k">def</span><span class="w"> </span><span class="nf">audit_name</span><span class="p">(</span><span class="n">name</span><span class="p">:</span> <span class="nb">str</span><span class="p">,</span> <span class="n">category</span><span class="p">:</span> <span class="nb">str</span> <span class="o">=</span> <span class="s2">&quot;plugin&quot;</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">str</span><span class="p">:</span>
</span><span id="L-288"><a href="#L-288"><span class="linenos">288</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-289"><a href="#L-289"><span class="linenos">289</span></a><span class="sd">    Audit the mol name to avoid the access to unexpected files</span>
</span><span id="L-290"><a href="#L-290"><span class="linenos">290</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-291"><a href="#L-291"><span class="linenos">291</span></a>    <span class="n">match</span> <span class="o">=</span> <span class="n">re</span><span class="o">.</span><span class="n">match</span><span class="p">(</span><span class="s2">&quot;^[A-Za-z0-9-_]+$&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span>
</span><span id="L-292"><a href="#L-292"><span class="linenos">292</span></a>    <span class="k">if</span> <span class="n">match</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="L-293"><a href="#L-293"><span class="linenos">293</span></a>        <span class="k">return</span> <span class="n">name</span>
</span><span id="L-294"><a href="#L-294"><span class="linenos">294</span></a>    <span class="n">match</span> <span class="o">=</span> <span class="n">re</span><span class="o">.</span><span class="n">match</span><span class="p">(</span><span class="sa">r</span><span class="s2">&quot;^\[([A-Za-z0-9-_]+) .*\]$&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span>
</span><span id="L-295"><a href="#L-295"><span class="linenos">295</span></a>    <span class="k">if</span> <span class="n">match</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="L-296"><a href="#L-296"><span class="linenos">296</span></a>        <span class="k">return</span> <span class="n">match</span><span class="o">.</span><span class="n">group</span><span class="p">(</span><span class="mi">1</span><span class="p">)</span>
</span><span id="L-297"><a href="#L-297"><span class="linenos">297</span></a>    <span class="k">raise</span> <span class="ne">ValueError</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Dubious </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2"> name: </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-298"><a href="#L-298"><span class="linenos">298</span></a>
</span><span id="L-299"><a href="#L-299"><span class="linenos">299</span></a>
</span><span id="L-300"><a href="#L-300"><span class="linenos">300</span></a><span class="k">def</span><span class="w"> </span><span class="nf">import_extra</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">name</span><span class="p">):</span>
</span><span id="L-301"><a href="#L-301"><span class="linenos">301</span></a>    <span class="n">logger</span> <span class="o">=</span> <span class="n">getLogger</span><span class="p">()</span>
</span><span id="L-302"><a href="#L-302"><span class="linenos">302</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Extra </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2"> plugin: </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-303"><a href="#L-303"><span class="linenos">303</span></a>    <span class="n">groupname</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot;genice3_</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="L-304"><a href="#L-304"><span class="linenos">304</span></a>    <span class="n">module</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="L-305"><a href="#L-305"><span class="linenos">305</span></a>    <span class="c1"># for ep in pr.iter_entry_points(group=groupname):</span>
</span><span id="L-306"><a href="#L-306"><span class="linenos">306</span></a>    <span class="k">for</span> <span class="n">ep</span> <span class="ow">in</span> <span class="n">entry_points</span><span class="p">(</span><span class="n">group</span><span class="o">=</span><span class="n">groupname</span><span class="p">):</span>
</span><span id="L-307"><a href="#L-307"><span class="linenos">307</span></a>        <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;    Entry point: </span><span class="si">{</span><span class="n">ep</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-308"><a href="#L-308"><span class="linenos">308</span></a>        <span class="k">if</span> <span class="n">ep</span><span class="o">.</span><span class="n">name</span> <span class="o">==</span> <span class="n">name</span><span class="p">:</span>
</span><span id="L-309"><a href="#L-309"><span class="linenos">309</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;      Loading </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">...&quot;</span><span class="p">)</span>
</span><span id="L-310"><a href="#L-310"><span class="linenos">310</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">ep</span><span class="o">.</span><span class="n">load</span><span class="p">()</span>
</span><span id="L-311"><a href="#L-311"><span class="linenos">311</span></a>    <span class="k">if</span> <span class="n">module</span> <span class="ow">is</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="L-312"><a href="#L-312"><span class="linenos">312</span></a>        <span class="k">raise</span> <span class="ne">ImportError</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Nonexistent or failed to load the </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2"> module: </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-313"><a href="#L-313"><span class="linenos">313</span></a>    <span class="k">return</span> <span class="n">module</span>
</span><span id="L-314"><a href="#L-314"><span class="linenos">314</span></a>
</span><span id="L-315"><a href="#L-315"><span class="linenos">315</span></a>
</span><span id="L-316"><a href="#L-316"><span class="linenos">316</span></a><span class="k">def</span><span class="w"> </span><span class="nf">safe_import</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">name</span><span class="p">):</span>
</span><span id="L-317"><a href="#L-317"><span class="linenos">317</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-318"><a href="#L-318"><span class="linenos">318</span></a><span class="sd">    Load a plugin.</span>
</span><span id="L-319"><a href="#L-319"><span class="linenos">319</span></a>
</span><span id="L-320"><a href="#L-320"><span class="linenos">320</span></a><span class="sd">    The plugins can exist either in the system, as a extra plugin, or in the</span>
</span><span id="L-321"><a href="#L-321"><span class="linenos">321</span></a><span class="sd">    local folder.</span>
</span><span id="L-322"><a href="#L-322"><span class="linenos">322</span></a>
</span><span id="L-323"><a href="#L-323"><span class="linenos">323</span></a><span class="sd">    category: The type of the plugin; &quot;lattice&quot;, &quot;format&quot;, &quot;molecule&quot;, or &quot;loader&quot;.</span>
</span><span id="L-324"><a href="#L-324"><span class="linenos">324</span></a><span class="sd">    name:     The name of the plugin.</span>
</span><span id="L-325"><a href="#L-325"><span class="linenos">325</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-326"><a href="#L-326"><span class="linenos">326</span></a>    <span class="n">logger</span> <span class="o">=</span> <span class="n">getLogger</span><span class="p">()</span>
</span><span id="L-327"><a href="#L-327"><span class="linenos">327</span></a>    <span class="k">if</span> <span class="n">category</span> <span class="ow">not</span> <span class="ow">in</span> <span class="p">(</span><span class="s2">&quot;exporter&quot;</span><span class="p">,</span> <span class="s2">&quot;molecule&quot;</span><span class="p">,</span> <span class="s2">&quot;unitcell&quot;</span><span class="p">,</span> <span class="s2">&quot;group&quot;</span><span class="p">):</span>
</span><span id="L-328"><a href="#L-328"><span class="linenos">328</span></a>        <span class="k">raise</span> <span class="ne">ValueError</span><span class="p">(</span>
</span><span id="L-329"><a href="#L-329"><span class="linenos">329</span></a>            <span class="sa">f</span><span class="s2">&quot;category must be &#39;exporter&#39;, &#39;molecule&#39;, &#39;unitcell&#39;, or &#39;group&#39;, got: </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="L-330"><a href="#L-330"><span class="linenos">330</span></a>        <span class="p">)</span>
</span><span id="L-331"><a href="#L-331"><span class="linenos">331</span></a>
</span><span id="L-332"><a href="#L-332"><span class="linenos">332</span></a>    <span class="c1"># single ? as a plugin name ==&gt; show descriptions (list all)</span>
</span><span id="L-333"><a href="#L-333"><span class="linenos">333</span></a>    <span class="k">if</span> <span class="n">name</span> <span class="o">==</span> <span class="s2">&quot;?&quot;</span><span class="p">:</span>
</span><span id="L-334"><a href="#L-334"><span class="linenos">334</span></a>        <span class="nb">print</span><span class="p">(</span><span class="n">descriptions</span><span class="p">(</span><span class="n">category</span><span class="p">))</span>
</span><span id="L-335"><a href="#L-335"><span class="linenos">335</span></a>        <span class="n">sys</span><span class="o">.</span><span class="n">exit</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span>
</span><span id="L-336"><a href="#L-336"><span class="linenos">336</span></a>
</span><span id="L-337"><a href="#L-337"><span class="linenos">337</span></a>    <span class="c1"># SYMBOL? ==&gt; show usage for that plugin (then exit)</span>
</span><span id="L-338"><a href="#L-338"><span class="linenos">338</span></a>    <span class="n">usage</span> <span class="o">=</span> <span class="kc">False</span>
</span><span id="L-339"><a href="#L-339"><span class="linenos">339</span></a>    <span class="k">if</span> <span class="nb">len</span><span class="p">(</span><span class="n">name</span><span class="p">)</span> <span class="o">&gt;</span> <span class="mi">1</span> <span class="ow">and</span> <span class="n">name</span><span class="p">[</span><span class="o">-</span><span class="mi">1</span><span class="p">]</span> <span class="o">==</span> <span class="s2">&quot;?&quot;</span><span class="p">:</span>
</span><span id="L-340"><a href="#L-340"><span class="linenos">340</span></a>        <span class="n">usage</span> <span class="o">=</span> <span class="kc">True</span>
</span><span id="L-341"><a href="#L-341"><span class="linenos">341</span></a>        <span class="n">name</span> <span class="o">=</span> <span class="n">name</span><span class="p">[:</span><span class="o">-</span><span class="mi">1</span><span class="p">]</span>
</span><span id="L-342"><a href="#L-342"><span class="linenos">342</span></a>
</span><span id="L-343"><a href="#L-343"><span class="linenos">343</span></a>    <span class="n">module_name</span> <span class="o">=</span> <span class="n">audit_name</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="n">category</span><span class="p">)</span>
</span><span id="L-344"><a href="#L-344"><span class="linenos">344</span></a>
</span><span id="L-345"><a href="#L-345"><span class="linenos">345</span></a>    <span class="n">module</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="L-346"><a href="#L-346"><span class="linenos">346</span></a>    <span class="n">fullname</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">module_name</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="L-347"><a href="#L-347"><span class="linenos">347</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Try to Load a local module: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-348"><a href="#L-348"><span class="linenos">348</span></a>    <span class="c1"># まずカレントディレクトリを path に挿入して試す（実行ディレクトリの group/ 等を読むため）</span>
</span><span id="L-349"><a href="#L-349"><span class="linenos">349</span></a>    <span class="n">cwd</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">getcwd</span><span class="p">()</span>
</span><span id="L-350"><a href="#L-350"><span class="linenos">350</span></a>    <span class="n">path_inserted</span> <span class="o">=</span> <span class="n">cwd</span> <span class="ow">not</span> <span class="ow">in</span> <span class="n">sys</span><span class="o">.</span><span class="n">path</span>
</span><span id="L-351"><a href="#L-351"><span class="linenos">351</span></a>    <span class="k">if</span> <span class="n">path_inserted</span><span class="p">:</span>
</span><span id="L-352"><a href="#L-352"><span class="linenos">352</span></a>        <span class="n">sys</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span> <span class="n">cwd</span><span class="p">)</span>
</span><span id="L-353"><a href="#L-353"><span class="linenos">353</span></a>    <span class="k">try</span><span class="p">:</span>
</span><span id="L-354"><a href="#L-354"><span class="linenos">354</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="L-355"><a href="#L-355"><span class="linenos">355</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="n">fullname</span><span class="p">)</span>
</span><span id="L-356"><a href="#L-356"><span class="linenos">356</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="s2">&quot;Succeeded (local from cwd or path).&quot;</span><span class="p">)</span>
</span><span id="L-357"><a href="#L-357"><span class="linenos">357</span></a>        <span class="k">except</span> <span class="ne">ModuleNotFoundError</span><span class="p">:</span>
</span><span id="L-358"><a href="#L-358"><span class="linenos">358</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Module not found: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-359"><a href="#L-359"><span class="linenos">359</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="L-360"><a href="#L-360"><span class="linenos">360</span></a>        <span class="k">except</span> <span class="ne">ImportError</span> <span class="k">as</span> <span class="n">e</span><span class="p">:</span>
</span><span id="L-361"><a href="#L-361"><span class="linenos">361</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">error</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Error importing module </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">: </span><span class="si">{</span><span class="nb">str</span><span class="p">(</span><span class="n">e</span><span class="p">)</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-362"><a href="#L-362"><span class="linenos">362</span></a>            <span class="k">raise</span>
</span><span id="L-363"><a href="#L-363"><span class="linenos">363</span></a>    <span class="k">finally</span><span class="p">:</span>
</span><span id="L-364"><a href="#L-364"><span class="linenos">364</span></a>        <span class="k">if</span> <span class="n">path_inserted</span> <span class="ow">and</span> <span class="n">sys</span><span class="o">.</span><span class="n">path</span> <span class="ow">and</span> <span class="n">sys</span><span class="o">.</span><span class="n">path</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span> <span class="o">==</span> <span class="n">cwd</span><span class="p">:</span>
</span><span id="L-365"><a href="#L-365"><span class="linenos">365</span></a>            <span class="n">sys</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span>
</span><span id="L-366"><a href="#L-366"><span class="linenos">366</span></a>    <span class="k">if</span> <span class="n">module</span> <span class="ow">is</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="L-367"><a href="#L-367"><span class="linenos">367</span></a>        <span class="n">fullname</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot;genice3.</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">module_name</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="L-368"><a href="#L-368"><span class="linenos">368</span></a>        <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Try to load a system module: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-369"><a href="#L-369"><span class="linenos">369</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="L-370"><a href="#L-370"><span class="linenos">370</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="n">fullname</span><span class="p">)</span>
</span><span id="L-371"><a href="#L-371"><span class="linenos">371</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="s2">&quot;Succeeded.&quot;</span><span class="p">)</span>
</span><span id="L-372"><a href="#L-372"><span class="linenos">372</span></a>        <span class="k">except</span> <span class="ne">ModuleNotFoundError</span><span class="p">:</span>
</span><span id="L-373"><a href="#L-373"><span class="linenos">373</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Module not found: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-374"><a href="#L-374"><span class="linenos">374</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="L-375"><a href="#L-375"><span class="linenos">375</span></a>        <span class="k">except</span> <span class="ne">ImportError</span> <span class="k">as</span> <span class="n">e</span><span class="p">:</span>
</span><span id="L-376"><a href="#L-376"><span class="linenos">376</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">error</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Error importing module </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">: </span><span class="si">{</span><span class="nb">str</span><span class="p">(</span><span class="n">e</span><span class="p">)</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-377"><a href="#L-377"><span class="linenos">377</span></a>            <span class="k">raise</span>
</span><span id="L-378"><a href="#L-378"><span class="linenos">378</span></a>    <span class="k">if</span> <span class="n">module</span> <span class="ow">is</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="L-379"><a href="#L-379"><span class="linenos">379</span></a>        <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Try to load an extra module: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-380"><a href="#L-380"><span class="linenos">380</span></a>        <span class="n">module</span> <span class="o">=</span> <span class="n">import_extra</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">module_name</span><span class="p">)</span>
</span><span id="L-381"><a href="#L-381"><span class="linenos">381</span></a>        <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="s2">&quot;Succeeded.&quot;</span><span class="p">)</span>
</span><span id="L-382"><a href="#L-382"><span class="linenos">382</span></a>
</span><span id="L-383"><a href="#L-383"><span class="linenos">383</span></a>    <span class="k">if</span> <span class="n">usage</span><span class="p">:</span>
</span><span id="L-384"><a href="#L-384"><span class="linenos">384</span></a>        <span class="k">if</span> <span class="s2">&quot;desc&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="L-385"><a href="#L-385"><span class="linenos">385</span></a>            <span class="n">d</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span>
</span><span id="L-386"><a href="#L-386"><span class="linenos">386</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Usage for &#39;</span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&#39; plugin&quot;</span><span class="p">)</span>
</span><span id="L-387"><a href="#L-387"><span class="linenos">387</span></a>            <span class="k">if</span> <span class="n">category</span> <span class="o">==</span> <span class="s2">&quot;unitcell&quot;</span> <span class="ow">and</span> <span class="n">d</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;options&quot;</span><span class="p">):</span>
</span><span id="L-388"><a href="#L-388"><span class="linenos">388</span></a>                <span class="n">u</span> <span class="o">=</span> <span class="n">format_unitcell_usage</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="n">d</span><span class="p">[</span><span class="s2">&quot;options&quot;</span><span class="p">])</span>
</span><span id="L-389"><a href="#L-389"><span class="linenos">389</span></a>                <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;CLI:  &quot;</span><span class="p">,</span> <span class="n">u</span><span class="p">[</span><span class="s2">&quot;cli&quot;</span><span class="p">])</span>
</span><span id="L-390"><a href="#L-390"><span class="linenos">390</span></a>                <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;API:  &quot;</span><span class="p">,</span> <span class="n">u</span><span class="p">[</span><span class="s2">&quot;api&quot;</span><span class="p">])</span>
</span><span id="L-391"><a href="#L-391"><span class="linenos">391</span></a>                <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;YAML:</span><span class="se">\n</span><span class="s2">&quot;</span><span class="p">,</span> <span class="n">u</span><span class="p">[</span><span class="s2">&quot;yaml&quot;</span><span class="p">])</span>
</span><span id="L-392"><a href="#L-392"><span class="linenos">392</span></a>            <span class="k">elif</span> <span class="n">d</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;usage&quot;</span><span class="p">):</span>
</span><span id="L-393"><a href="#L-393"><span class="linenos">393</span></a>                <span class="nb">print</span><span class="p">(</span><span class="n">d</span><span class="p">[</span><span class="s2">&quot;usage&quot;</span><span class="p">])</span>
</span><span id="L-394"><a href="#L-394"><span class="linenos">394</span></a>            <span class="k">else</span><span class="p">:</span>
</span><span id="L-395"><a href="#L-395"><span class="linenos">395</span></a>                <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;(no usage)&quot;</span><span class="p">)</span>
</span><span id="L-396"><a href="#L-396"><span class="linenos">396</span></a>            <span class="n">sys</span><span class="o">.</span><span class="n">exit</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span>
</span><span id="L-397"><a href="#L-397"><span class="linenos">397</span></a>
</span><span id="L-398"><a href="#L-398"><span class="linenos">398</span></a>    <span class="k">return</span> <span class="n">module</span>
</span><span id="L-399"><a href="#L-399"><span class="linenos">399</span></a>
</span><span id="L-400"><a href="#L-400"><span class="linenos">400</span></a>
</span><span id="L-401"><a href="#L-401"><span class="linenos">401</span></a><span class="k">def</span><span class="w"> </span><span class="nf">UnitCell</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
</span><span id="L-402"><a href="#L-402"><span class="linenos">402</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-403"><a href="#L-403"><span class="linenos">403</span></a><span class="sd">    Shortcut for safe_import.</span>
</span><span id="L-404"><a href="#L-404"><span class="linenos">404</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-405"><a href="#L-405"><span class="linenos">405</span></a>    <span class="k">return</span> <span class="n">safe_import</span><span class="p">(</span><span class="s2">&quot;unitcell&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span><span class="o">.</span><span class="n">UnitCell</span><span class="p">(</span><span class="o">**</span><span class="n">kwargs</span><span class="p">)</span>
</span><span id="L-406"><a href="#L-406"><span class="linenos">406</span></a>
</span><span id="L-407"><a href="#L-407"><span class="linenos">407</span></a>
</span><span id="L-408"><a href="#L-408"><span class="linenos">408</span></a><span class="k">def</span><span class="w"> </span><span class="nf">Molecule</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
</span><span id="L-409"><a href="#L-409"><span class="linenos">409</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-410"><a href="#L-410"><span class="linenos">410</span></a><span class="sd">    Shortcut for safe_import.</span>
</span><span id="L-411"><a href="#L-411"><span class="linenos">411</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-412"><a href="#L-412"><span class="linenos">412</span></a>    <span class="k">return</span> <span class="n">safe_import</span><span class="p">(</span><span class="s2">&quot;molecule&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span><span class="o">.</span><span class="n">Molecule</span><span class="p">(</span><span class="o">**</span><span class="n">kwargs</span><span class="p">)</span>
</span><span id="L-413"><a href="#L-413"><span class="linenos">413</span></a>
</span><span id="L-414"><a href="#L-414"><span class="linenos">414</span></a>
</span><span id="L-415"><a href="#L-415"><span class="linenos">415</span></a><span class="k">def</span><span class="w"> </span><span class="nf">Exporter</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
</span><span id="L-416"><a href="#L-416"><span class="linenos">416</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-417"><a href="#L-417"><span class="linenos">417</span></a><span class="sd">    Shortcut for safe_import.</span>
</span><span id="L-418"><a href="#L-418"><span class="linenos">418</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-419"><a href="#L-419"><span class="linenos">419</span></a>    <span class="k">return</span> <span class="n">safe_import</span><span class="p">(</span><span class="s2">&quot;exporter&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span>
</span><span id="L-420"><a href="#L-420"><span class="linenos">420</span></a>
</span><span id="L-421"><a href="#L-421"><span class="linenos">421</span></a>
</span><span id="L-422"><a href="#L-422"><span class="linenos">422</span></a><span class="k">def</span><span class="w"> </span><span class="nf">Group</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
</span><span id="L-423"><a href="#L-423"><span class="linenos">423</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-424"><a href="#L-424"><span class="linenos">424</span></a><span class="sd">    Shortcut for safe_import.</span>
</span><span id="L-425"><a href="#L-425"><span class="linenos">425</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-426"><a href="#L-426"><span class="linenos">426</span></a>    <span class="k">return</span> <span class="n">safe_import</span><span class="p">(</span><span class="s2">&quot;group&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span><span class="o">.</span><span class="n">Group</span><span class="p">(</span><span class="o">**</span><span class="n">kwargs</span><span class="p">)</span>
</span><span id="L-427"><a href="#L-427"><span class="linenos">427</span></a>
</span><span id="L-428"><a href="#L-428"><span class="linenos">428</span></a>
</span><span id="L-429"><a href="#L-429"><span class="linenos">429</span></a><span class="k">def</span><span class="w"> </span><span class="nf">get_exporter_format_rows</span><span class="p">(</span><span class="n">category</span><span class="o">=</span><span class="s2">&quot;exporter&quot;</span><span class="p">,</span> <span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s2">&quot;system&quot;</span><span class="p">,</span> <span class="s2">&quot;extra&quot;</span><span class="p">,</span> <span class="s2">&quot;local&quot;</span><span class="p">)):</span>
</span><span id="L-430"><a href="#L-430"><span class="linenos">430</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="L-431"><a href="#L-431"><span class="linenos">431</span></a><span class="sd">    Collect format_desc from all exporter plugins and return rows for the README table.</span>
</span><span id="L-432"><a href="#L-432"><span class="linenos">432</span></a>
</span><span id="L-433"><a href="#L-433"><span class="linenos">433</span></a><span class="sd">    Each exporter module may define a ``format_desc`` dict with keys:</span>
</span><span id="L-434"><a href="#L-434"><span class="linenos">434</span></a><span class="sd">      aliases: list of option names (e.g. [&quot;g&quot;, &quot;gromacs&quot;])</span>
</span><span id="L-435"><a href="#L-435"><span class="linenos">435</span></a><span class="sd">      application: str (markdown allowed)</span>
</span><span id="L-436"><a href="#L-436"><span class="linenos">436</span></a><span class="sd">      extension: str (e.g. &quot;.gro&quot;)</span>
</span><span id="L-437"><a href="#L-437"><span class="linenos">437</span></a><span class="sd">      water: str (e.g. &quot;Atomic positions&quot;)</span>
</span><span id="L-438"><a href="#L-438"><span class="linenos">438</span></a><span class="sd">      solute: str</span>
</span><span id="L-439"><a href="#L-439"><span class="linenos">439</span></a><span class="sd">      hb: str (e.g. &quot;none&quot;, &quot;o&quot;, &quot;auto&quot;)</span>
</span><span id="L-440"><a href="#L-440"><span class="linenos">440</span></a><span class="sd">      remarks: str</span>
</span><span id="L-441"><a href="#L-441"><span class="linenos">441</span></a><span class="sd">      suboptions: str (optional; short description of :key value options, e.g. &quot;water_model: 3site, 4site, 6site, tip4p&quot;)</span>
</span><span id="L-442"><a href="#L-442"><span class="linenos">442</span></a>
</span><span id="L-443"><a href="#L-443"><span class="linenos">443</span></a><span class="sd">    Returns a list of dicts with keys name, application, extension, water, solute, hb, remarks, suboptions.</span>
</span><span id="L-444"><a href="#L-444"><span class="linenos">444</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="L-445"><a href="#L-445"><span class="linenos">445</span></a>    <span class="n">logger</span> <span class="o">=</span> <span class="n">getLogger</span><span class="p">()</span>
</span><span id="L-446"><a href="#L-446"><span class="linenos">446</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="n">scan</span><span class="p">(</span><span class="n">category</span><span class="p">)</span>
</span><span id="L-447"><a href="#L-447"><span class="linenos">447</span></a>    <span class="n">rows</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="L-448"><a href="#L-448"><span class="linenos">448</span></a>    <span class="n">seen</span> <span class="o">=</span> <span class="nb">set</span><span class="p">()</span>
</span><span id="L-449"><a href="#L-449"><span class="linenos">449</span></a>
</span><span id="L-450"><a href="#L-450"><span class="linenos">450</span></a>    <span class="k">for</span> <span class="n">group</span> <span class="ow">in</span> <span class="n">groups</span><span class="p">:</span>
</span><span id="L-451"><a href="#L-451"><span class="linenos">451</span></a>        <span class="k">for</span> <span class="n">name</span> <span class="ow">in</span> <span class="n">mods</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">group</span><span class="p">,</span> <span class="p">[]):</span>
</span><span id="L-452"><a href="#L-452"><span class="linenos">452</span></a>            <span class="k">if</span> <span class="n">name</span> <span class="ow">in</span> <span class="n">seen</span><span class="p">:</span>
</span><span id="L-453"><a href="#L-453"><span class="linenos">453</span></a>                <span class="k">continue</span>
</span><span id="L-454"><a href="#L-454"><span class="linenos">454</span></a>            <span class="k">try</span><span class="p">:</span>
</span><span id="L-455"><a href="#L-455"><span class="linenos">455</span></a>                <span class="k">if</span> <span class="n">group</span> <span class="o">==</span> <span class="s2">&quot;system&quot;</span><span class="p">:</span>
</span><span id="L-456"><a href="#L-456"><span class="linenos">456</span></a>                    <span class="n">mod</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;genice3.</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-457"><a href="#L-457"><span class="linenos">457</span></a>                <span class="k">elif</span> <span class="n">group</span> <span class="o">==</span> <span class="s2">&quot;extra&quot;</span><span class="p">:</span>
</span><span id="L-458"><a href="#L-458"><span class="linenos">458</span></a>                    <span class="n">mod</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="L-459"><a href="#L-459"><span class="linenos">459</span></a>                    <span class="k">for</span> <span class="n">ep</span> <span class="ow">in</span> <span class="n">entry_points</span><span class="p">(</span><span class="n">group</span><span class="o">=</span><span class="sa">f</span><span class="s2">&quot;genice3_</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">):</span>
</span><span id="L-460"><a href="#L-460"><span class="linenos">460</span></a>                        <span class="k">if</span> <span class="n">ep</span><span class="o">.</span><span class="n">name</span> <span class="o">==</span> <span class="n">name</span><span class="p">:</span>
</span><span id="L-461"><a href="#L-461"><span class="linenos">461</span></a>                            <span class="n">mod</span> <span class="o">=</span> <span class="n">ep</span><span class="o">.</span><span class="n">load</span><span class="p">()</span>
</span><span id="L-462"><a href="#L-462"><span class="linenos">462</span></a>                            <span class="k">break</span>
</span><span id="L-463"><a href="#L-463"><span class="linenos">463</span></a>                    <span class="k">if</span> <span class="n">mod</span> <span class="ow">is</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="L-464"><a href="#L-464"><span class="linenos">464</span></a>                        <span class="k">continue</span>
</span><span id="L-465"><a href="#L-465"><span class="linenos">465</span></a>                <span class="k">else</span><span class="p">:</span>
</span><span id="L-466"><a href="#L-466"><span class="linenos">466</span></a>                    <span class="k">try</span><span class="p">:</span>
</span><span id="L-467"><a href="#L-467"><span class="linenos">467</span></a>                        <span class="n">mod</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-468"><a href="#L-468"><span class="linenos">468</span></a>                    <span class="k">except</span> <span class="ne">ModuleNotFoundError</span><span class="p">:</span>
</span><span id="L-469"><a href="#L-469"><span class="linenos">469</span></a>                        <span class="k">continue</span>
</span><span id="L-470"><a href="#L-470"><span class="linenos">470</span></a>                <span class="k">if</span> <span class="ow">not</span> <span class="nb">hasattr</span><span class="p">(</span><span class="n">mod</span><span class="p">,</span> <span class="s2">&quot;format_desc&quot;</span><span class="p">):</span>
</span><span id="L-471"><a href="#L-471"><span class="linenos">471</span></a>                    <span class="k">continue</span>
</span><span id="L-472"><a href="#L-472"><span class="linenos">472</span></a>                <span class="n">fd</span> <span class="o">=</span> <span class="n">mod</span><span class="o">.</span><span class="n">format_desc</span>
</span><span id="L-473"><a href="#L-473"><span class="linenos">473</span></a>                <span class="n">aliases</span> <span class="o">=</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;aliases&quot;</span><span class="p">,</span> <span class="p">[</span><span class="n">name</span><span class="p">])</span>
</span><span id="L-474"><a href="#L-474"><span class="linenos">474</span></a>                <span class="n">name_col</span> <span class="o">=</span> <span class="s2">&quot;, &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;`</span><span class="si">{</span><span class="n">a</span><span class="si">}</span><span class="s2">`&quot;</span> <span class="k">for</span> <span class="n">a</span> <span class="ow">in</span> <span class="n">aliases</span><span class="p">)</span>
</span><span id="L-475"><a href="#L-475"><span class="linenos">475</span></a>                <span class="n">rows</span><span class="o">.</span><span class="n">append</span><span class="p">(</span>
</span><span id="L-476"><a href="#L-476"><span class="linenos">476</span></a>                    <span class="p">{</span>
</span><span id="L-477"><a href="#L-477"><span class="linenos">477</span></a>                        <span class="s2">&quot;name&quot;</span><span class="p">:</span> <span class="n">name_col</span><span class="p">,</span>
</span><span id="L-478"><a href="#L-478"><span class="linenos">478</span></a>                        <span class="s2">&quot;application&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;application&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="L-479"><a href="#L-479"><span class="linenos">479</span></a>                        <span class="s2">&quot;extension&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;extension&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="L-480"><a href="#L-480"><span class="linenos">480</span></a>                        <span class="s2">&quot;water&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;water&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="L-481"><a href="#L-481"><span class="linenos">481</span></a>                        <span class="s2">&quot;solute&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;solute&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="L-482"><a href="#L-482"><span class="linenos">482</span></a>                        <span class="s2">&quot;hb&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;hb&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="L-483"><a href="#L-483"><span class="linenos">483</span></a>                        <span class="s2">&quot;remarks&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;remarks&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="L-484"><a href="#L-484"><span class="linenos">484</span></a>                        <span class="s2">&quot;suboptions&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;suboptions&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="L-485"><a href="#L-485"><span class="linenos">485</span></a>                    <span class="p">}</span>
</span><span id="L-486"><a href="#L-486"><span class="linenos">486</span></a>                <span class="p">)</span>
</span><span id="L-487"><a href="#L-487"><span class="linenos">487</span></a>                <span class="n">seen</span><span class="o">.</span><span class="n">add</span><span class="p">(</span><span class="n">name</span><span class="p">)</span>
</span><span id="L-488"><a href="#L-488"><span class="linenos">488</span></a>            <span class="k">except</span> <span class="ne">Exception</span> <span class="k">as</span> <span class="n">e</span><span class="p">:</span>
</span><span id="L-489"><a href="#L-489"><span class="linenos">489</span></a>                <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Skip </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2"> for format table: </span><span class="si">{</span><span class="n">e</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="L-490"><a href="#L-490"><span class="linenos">490</span></a>    <span class="k">return</span> <span class="n">rows</span>
</span><span id="L-491"><a href="#L-491"><span class="linenos">491</span></a>
</span><span id="L-492"><a href="#L-492"><span class="linenos">492</span></a>
</span><span id="L-493"><a href="#L-493"><span class="linenos">493</span></a><span class="k">if</span> <span class="vm">__name__</span> <span class="o">==</span> <span class="s2">&quot;__main__&quot;</span><span class="p">:</span>
</span><span id="L-494"><a href="#L-494"><span class="linenos">494</span></a>    <span class="n">basicConfig</span><span class="p">(</span><span class="n">level</span><span class="o">=</span><span class="n">INFO</span><span class="p">)</span>
</span><span id="L-495"><a href="#L-495"><span class="linenos">495</span></a>    <span class="k">if</span> <span class="nb">len</span><span class="p">(</span><span class="n">sys</span><span class="o">.</span><span class="n">argv</span><span class="p">)</span> <span class="o">==</span> <span class="mi">1</span><span class="p">:</span>
</span><span id="L-496"><a href="#L-496"><span class="linenos">496</span></a>        <span class="n">cats</span> <span class="o">=</span> <span class="p">(</span><span class="s2">&quot;lattice&quot;</span><span class="p">,</span> <span class="s2">&quot;format&quot;</span><span class="p">,</span> <span class="s2">&quot;molecule&quot;</span><span class="p">,</span> <span class="s2">&quot;loader&quot;</span><span class="p">)</span>
</span><span id="L-497"><a href="#L-497"><span class="linenos">497</span></a>    <span class="k">else</span><span class="p">:</span>
</span><span id="L-498"><a href="#L-498"><span class="linenos">498</span></a>        <span class="n">cats</span> <span class="o">=</span> <span class="n">sys</span><span class="o">.</span><span class="n">argv</span><span class="p">[</span><span class="mi">1</span><span class="p">:]</span>
</span><span id="L-499"><a href="#L-499"><span class="linenos">499</span></a>    <span class="n">modules</span> <span class="o">=</span> <span class="p">{</span><span class="n">cat</span><span class="p">:</span> <span class="n">scan</span><span class="p">(</span><span class="n">cat</span><span class="p">)</span> <span class="k">for</span> <span class="n">cat</span> <span class="ow">in</span> <span class="n">cats</span><span class="p">}</span>
</span><span id="L-500"><a href="#L-500"><span class="linenos">500</span></a>    <span class="nb">print</span><span class="p">(</span><span class="n">modules</span><span class="p">)</span>
</span></pre></div>


            </section>
                <section id="format_unitcell_usage">
                            <input id="format_unitcell_usage-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">format_unitcell_usage</span><span class="signature pdoc-code multiline">(<span class="param">	<span class="n">unitcell_name</span><span class="p">:</span> <span class="nb">str</span>,</span><span class="param">	<span class="n">options</span><span class="p">:</span> <span class="n">Sequence</span><span class="p">[</span><span class="n">Union</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">],</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]]</span></span><span class="return-annotation">) -> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]</span>:</span></span>

                <label class="view-source-button" for="format_unitcell_usage-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#format_unitcell_usage"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="format_unitcell_usage-50"><a href="#format_unitcell_usage-50"><span class="linenos">50</span></a><span class="k">def</span><span class="w"> </span><span class="nf">format_unitcell_usage</span><span class="p">(</span>
</span><span id="format_unitcell_usage-51"><a href="#format_unitcell_usage-51"><span class="linenos">51</span></a>    <span class="n">unitcell_name</span><span class="p">:</span> <span class="nb">str</span><span class="p">,</span> <span class="n">options</span><span class="p">:</span> <span class="n">Sequence</span><span class="p">[</span><span class="n">Union</span><span class="p">[</span><span class="n">Tuple</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">],</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="n">Any</span><span class="p">]]]</span>
</span><span id="format_unitcell_usage-52"><a href="#format_unitcell_usage-52"><span class="linenos">52</span></a><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Dict</span><span class="p">[</span><span class="nb">str</span><span class="p">,</span> <span class="nb">str</span><span class="p">]:</span>
</span><span id="format_unitcell_usage-53"><a href="#format_unitcell_usage-53"><span class="linenos">53</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="format_unitcell_usage-54"><a href="#format_unitcell_usage-54"><span class="linenos">54</span></a><span class="sd">    options 構造体から CLI / API / YAML の 3 表記を生成する。</span>
</span><span id="format_unitcell_usage-55"><a href="#format_unitcell_usage-55"><span class="linenos">55</span></a><span class="sd">    Returns:</span>
</span><span id="format_unitcell_usage-56"><a href="#format_unitcell_usage-56"><span class="linenos">56</span></a><span class="sd">        {&quot;cli&quot;: &quot;...&quot;, &quot;api&quot;: &quot;...&quot;, &quot;yaml&quot;: &quot;...&quot;}</span>
</span><span id="format_unitcell_usage-57"><a href="#format_unitcell_usage-57"><span class="linenos">57</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="format_unitcell_usage-58"><a href="#format_unitcell_usage-58"><span class="linenos">58</span></a>    <span class="n">opts</span> <span class="o">=</span> <span class="n">_normalize_unitcell_options</span><span class="p">(</span><span class="n">options</span><span class="p">)</span>
</span><span id="format_unitcell_usage-59"><a href="#format_unitcell_usage-59"><span class="linenos">59</span></a>    <span class="n">cli_parts</span> <span class="o">=</span> <span class="p">[</span><span class="sa">f</span><span class="s2">&quot;genice3 </span><span class="si">{</span><span class="n">unitcell_name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">]</span>
</span><span id="format_unitcell_usage-60"><a href="#format_unitcell_usage-60"><span class="linenos">60</span></a>    <span class="n">api_args</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="format_unitcell_usage-61"><a href="#format_unitcell_usage-61"><span class="linenos">61</span></a>    <span class="n">yaml_lines</span> <span class="o">=</span> <span class="p">[</span><span class="sa">f</span><span class="s2">&quot;unitcell:&quot;</span><span class="p">,</span> <span class="sa">f</span><span class="s2">&quot;  name: </span><span class="si">{</span><span class="n">unitcell_name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">]</span>
</span><span id="format_unitcell_usage-62"><a href="#format_unitcell_usage-62"><span class="linenos">62</span></a>    <span class="k">for</span> <span class="n">o</span> <span class="ow">in</span> <span class="n">opts</span><span class="p">:</span>
</span><span id="format_unitcell_usage-63"><a href="#format_unitcell_usage-63"><span class="linenos">63</span></a>        <span class="n">ex</span> <span class="o">=</span> <span class="n">o</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;example&quot;</span><span class="p">)</span>
</span><span id="format_unitcell_usage-64"><a href="#format_unitcell_usage-64"><span class="linenos">64</span></a>        <span class="n">ex_str</span> <span class="o">=</span> <span class="nb">str</span><span class="p">(</span><span class="n">ex</span><span class="p">)</span> <span class="k">if</span> <span class="n">ex</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span> <span class="k">else</span> <span class="s2">&quot;VALUE&quot;</span>
</span><span id="format_unitcell_usage-65"><a href="#format_unitcell_usage-65"><span class="linenos">65</span></a>        <span class="n">cli_parts</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;--</span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2"> </span><span class="si">{</span><span class="n">ex_str</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="format_unitcell_usage-66"><a href="#format_unitcell_usage-66"><span class="linenos">66</span></a>        <span class="k">if</span> <span class="n">o</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;required&quot;</span><span class="p">):</span>
</span><span id="format_unitcell_usage-67"><a href="#format_unitcell_usage-67"><span class="linenos">67</span></a>            <span class="n">cli_parts</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="s2">&quot;(required)&quot;</span><span class="p">)</span>
</span><span id="format_unitcell_usage-68"><a href="#format_unitcell_usage-68"><span class="linenos">68</span></a>        <span class="n">api_args</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">=</span><span class="si">{</span><span class="nb">repr</span><span class="p">(</span><span class="n">ex</span><span class="p">)</span><span class="si">}</span><span class="s2">&quot;</span> <span class="k">if</span> <span class="n">ex</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span> <span class="k">else</span> <span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">=None&quot;</span><span class="p">)</span>
</span><span id="format_unitcell_usage-69"><a href="#format_unitcell_usage-69"><span class="linenos">69</span></a>        <span class="n">yaml_lines</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;  </span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">: </span><span class="si">{</span><span class="n">ex</span><span class="si">}</span><span class="s2">&quot;</span> <span class="k">if</span> <span class="n">ex</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span> <span class="k">else</span> <span class="sa">f</span><span class="s2">&quot;  </span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">: ...&quot;</span><span class="p">)</span>
</span><span id="format_unitcell_usage-70"><a href="#format_unitcell_usage-70"><span class="linenos">70</span></a>    <span class="k">return</span> <span class="p">{</span>
</span><span id="format_unitcell_usage-71"><a href="#format_unitcell_usage-71"><span class="linenos">71</span></a>        <span class="s2">&quot;cli&quot;</span><span class="p">:</span> <span class="s2">&quot; &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">cli_parts</span><span class="p">)</span> <span class="o">+</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">  &quot;</span> <span class="o">+</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">  &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;--</span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;name&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">: </span><span class="si">{</span><span class="n">o</span><span class="p">[</span><span class="s1">&#39;help&#39;</span><span class="p">]</span><span class="si">}</span><span class="s2">&quot;</span> <span class="k">for</span> <span class="n">o</span> <span class="ow">in</span> <span class="n">opts</span><span class="p">),</span>
</span><span id="format_unitcell_usage-72"><a href="#format_unitcell_usage-72"><span class="linenos">72</span></a>        <span class="s2">&quot;api&quot;</span><span class="p">:</span> <span class="sa">f</span><span class="s1">&#39;UnitCell(&quot;</span><span class="si">{</span><span class="n">unitcell_name</span><span class="si">}</span><span class="s1">&quot;, &#39;</span> <span class="o">+</span> <span class="s2">&quot;, &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">api_args</span><span class="p">)</span> <span class="o">+</span> <span class="s2">&quot;)&quot;</span><span class="p">,</span>
</span><span id="format_unitcell_usage-73"><a href="#format_unitcell_usage-73"><span class="linenos">73</span></a>        <span class="s2">&quot;yaml&quot;</span><span class="p">:</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">&quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">yaml_lines</span><span class="p">),</span>
</span><span id="format_unitcell_usage-74"><a href="#format_unitcell_usage-74"><span class="linenos">74</span></a>    <span class="p">}</span>
</span></pre></div>


            <div class="docstring"><p>options 構造体から CLI / API / YAML の 3 表記を生成する。
Returns:
    {"cli": "...", "api": "...", "yaml": "..."}</p>
</div>


                </section>
                <section id="scan">
                            <input id="scan-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">scan</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">category</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="scan-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#scan"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="scan-92"><a href="#scan-92"><span class="linenos"> 92</span></a><span class="k">def</span><span class="w"> </span><span class="nf">scan</span><span class="p">(</span><span class="n">category</span><span class="p">):</span>
</span><span id="scan-93"><a href="#scan-93"><span class="linenos"> 93</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="scan-94"><a href="#scan-94"><span class="linenos"> 94</span></a><span class="sd">    Scan available plugins.</span>
</span><span id="scan-95"><a href="#scan-95"><span class="linenos"> 95</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="scan-96"><a href="#scan-96"><span class="linenos"> 96</span></a>    <span class="n">logger</span> <span class="o">=</span> <span class="n">getLogger</span><span class="p">()</span>
</span><span id="scan-97"><a href="#scan-97"><span class="linenos"> 97</span></a>
</span><span id="scan-98"><a href="#scan-98"><span class="linenos"> 98</span></a>    <span class="n">modules</span> <span class="o">=</span> <span class="p">{}</span>
</span><span id="scan-99"><a href="#scan-99"><span class="linenos"> 99</span></a>    <span class="n">desc</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="scan-100"><a href="#scan-100"><span class="linenos">100</span></a>    <span class="n">iswater</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="scan-101"><a href="#scan-101"><span class="linenos">101</span></a>    <span class="n">refs</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="scan-102"><a href="#scan-102"><span class="linenos">102</span></a>    <span class="n">tests</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="scan-103"><a href="#scan-103"><span class="linenos">103</span></a>
</span><span id="scan-104"><a href="#scan-104"><span class="linenos">104</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="se">\n</span><span class="s2">Predefined </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="scan-105"><a href="#scan-105"><span class="linenos">105</span></a>    <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;genice3.</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="scan-106"><a href="#scan-106"><span class="linenos">106</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="scan-107"><a href="#scan-107"><span class="linenos">107</span></a>    <span class="k">for</span> <span class="n">path</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">__path__</span><span class="p">:</span>
</span><span id="scan-108"><a href="#scan-108"><span class="linenos">108</span></a>        <span class="k">for</span> <span class="n">mod</span> <span class="ow">in</span> <span class="nb">sorted</span><span class="p">(</span><span class="n">glob</span><span class="o">.</span><span class="n">glob</span><span class="p">(</span><span class="n">path</span> <span class="o">+</span> <span class="s2">&quot;/*.py&quot;</span><span class="p">)):</span>
</span><span id="scan-109"><a href="#scan-109"><span class="linenos">109</span></a>            <span class="n">mod</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">basename</span><span class="p">(</span><span class="n">mod</span><span class="p">)[:</span><span class="o">-</span><span class="mi">3</span><span class="p">]</span>
</span><span id="scan-110"><a href="#scan-110"><span class="linenos">110</span></a>            <span class="k">if</span> <span class="n">mod</span><span class="p">[:</span><span class="mi">2</span><span class="p">]</span> <span class="o">!=</span> <span class="s2">&quot;__&quot;</span><span class="p">:</span>
</span><span id="scan-111"><a href="#scan-111"><span class="linenos">111</span></a>                <span class="n">mods</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">mod</span><span class="p">)</span>
</span><span id="scan-112"><a href="#scan-112"><span class="linenos">112</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="n">mods</span><span class="p">)</span>
</span><span id="scan-113"><a href="#scan-113"><span class="linenos">113</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;system&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">mods</span>
</span><span id="scan-114"><a href="#scan-114"><span class="linenos">114</span></a>
</span><span id="scan-115"><a href="#scan-115"><span class="linenos">115</span></a>    <span class="k">for</span> <span class="n">mod</span> <span class="ow">in</span> <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;system&quot;</span><span class="p">]:</span>
</span><span id="scan-116"><a href="#scan-116"><span class="linenos">116</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="scan-117"><a href="#scan-117"><span class="linenos">117</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;genice3.</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">mod</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="scan-118"><a href="#scan-118"><span class="linenos">118</span></a>            <span class="k">if</span> <span class="s2">&quot;desc&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="scan-119"><a href="#scan-119"><span class="linenos">119</span></a>                <span class="n">desc</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;brief&quot;</span><span class="p">]</span>
</span><span id="scan-120"><a href="#scan-120"><span class="linenos">120</span></a>                <span class="k">if</span> <span class="s2">&quot;ref&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="scan-121"><a href="#scan-121"><span class="linenos">121</span></a>                    <span class="n">refs</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;ref&quot;</span><span class="p">]</span>
</span><span id="scan-122"><a href="#scan-122"><span class="linenos">122</span></a>                <span class="k">if</span> <span class="s2">&quot;test&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="scan-123"><a href="#scan-123"><span class="linenos">123</span></a>                    <span class="n">tests</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;test&quot;</span><span class="p">]</span>
</span><span id="scan-124"><a href="#scan-124"><span class="linenos">124</span></a>            <span class="n">iswater</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">_is_water_module</span><span class="p">(</span><span class="n">module</span><span class="p">,</span> <span class="n">category</span><span class="p">)</span>
</span><span id="scan-125"><a href="#scan-125"><span class="linenos">125</span></a>        <span class="k">except</span> <span class="ne">BaseException</span><span class="p">:</span>
</span><span id="scan-126"><a href="#scan-126"><span class="linenos">126</span></a>            <span class="k">pass</span>
</span><span id="scan-127"><a href="#scan-127"><span class="linenos">127</span></a>
</span><span id="scan-128"><a href="#scan-128"><span class="linenos">128</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Extra </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="scan-129"><a href="#scan-129"><span class="linenos">129</span></a>    <span class="n">groupname</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot;genice3_</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="scan-130"><a href="#scan-130"><span class="linenos">130</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="scan-131"><a href="#scan-131"><span class="linenos">131</span></a>    <span class="c1"># for ep in pr.iter_entry_points(group=groupname):</span>
</span><span id="scan-132"><a href="#scan-132"><span class="linenos">132</span></a>    <span class="k">for</span> <span class="n">ep</span> <span class="ow">in</span> <span class="n">entry_points</span><span class="p">(</span><span class="n">group</span><span class="o">=</span><span class="n">groupname</span><span class="p">):</span>
</span><span id="scan-133"><a href="#scan-133"><span class="linenos">133</span></a>        <span class="n">mods</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">ep</span><span class="o">.</span><span class="n">name</span><span class="p">)</span>
</span><span id="scan-134"><a href="#scan-134"><span class="linenos">134</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="scan-135"><a href="#scan-135"><span class="linenos">135</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">ep</span><span class="o">.</span><span class="n">load</span><span class="p">()</span>
</span><span id="scan-136"><a href="#scan-136"><span class="linenos">136</span></a>            <span class="k">if</span> <span class="s2">&quot;desc&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="scan-137"><a href="#scan-137"><span class="linenos">137</span></a>                <span class="n">desc</span><span class="p">[</span><span class="n">ep</span><span class="o">.</span><span class="n">name</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;brief&quot;</span><span class="p">]</span>
</span><span id="scan-138"><a href="#scan-138"><span class="linenos">138</span></a>                <span class="k">if</span> <span class="s2">&quot;ref&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="scan-139"><a href="#scan-139"><span class="linenos">139</span></a>                    <span class="n">refs</span><span class="p">[</span><span class="n">ep</span><span class="o">.</span><span class="n">name</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;ref&quot;</span><span class="p">]</span>
</span><span id="scan-140"><a href="#scan-140"><span class="linenos">140</span></a>                <span class="k">if</span> <span class="s2">&quot;test&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="scan-141"><a href="#scan-141"><span class="linenos">141</span></a>                    <span class="n">tests</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;test&quot;</span><span class="p">]</span>
</span><span id="scan-142"><a href="#scan-142"><span class="linenos">142</span></a>            <span class="n">iswater</span><span class="p">[</span><span class="n">ep</span><span class="o">.</span><span class="n">name</span><span class="p">]</span> <span class="o">=</span> <span class="n">_is_water_module</span><span class="p">(</span><span class="n">module</span><span class="p">,</span> <span class="n">category</span><span class="p">)</span>
</span><span id="scan-143"><a href="#scan-143"><span class="linenos">143</span></a>        <span class="k">except</span> <span class="ne">BaseException</span><span class="p">:</span>
</span><span id="scan-144"><a href="#scan-144"><span class="linenos">144</span></a>            <span class="k">pass</span>
</span><span id="scan-145"><a href="#scan-145"><span class="linenos">145</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="n">mods</span><span class="p">)</span>
</span><span id="scan-146"><a href="#scan-146"><span class="linenos">146</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;extra&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">mods</span>
</span><span id="scan-147"><a href="#scan-147"><span class="linenos">147</span></a>
</span><span id="scan-148"><a href="#scan-148"><span class="linenos">148</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Local </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="scan-149"><a href="#scan-149"><span class="linenos">149</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="p">[</span>
</span><span id="scan-150"><a href="#scan-150"><span class="linenos">150</span></a>        <span class="n">os</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">basename</span><span class="p">(</span><span class="n">mod</span><span class="p">)[:</span><span class="o">-</span><span class="mi">3</span><span class="p">]</span> <span class="k">for</span> <span class="n">mod</span> <span class="ow">in</span> <span class="nb">sorted</span><span class="p">(</span><span class="n">glob</span><span class="o">.</span><span class="n">glob</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;./</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">/*.py&quot;</span><span class="p">))</span>
</span><span id="scan-151"><a href="#scan-151"><span class="linenos">151</span></a>    <span class="p">]</span>
</span><span id="scan-152"><a href="#scan-152"><span class="linenos">152</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="n">mods</span><span class="p">)</span>
</span><span id="scan-153"><a href="#scan-153"><span class="linenos">153</span></a>    <span class="k">for</span> <span class="n">mod</span> <span class="ow">in</span> <span class="n">mods</span><span class="p">:</span>
</span><span id="scan-154"><a href="#scan-154"><span class="linenos">154</span></a>        <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">mod</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="scan-155"><a href="#scan-155"><span class="linenos">155</span></a>        <span class="k">if</span> <span class="s2">&quot;desc&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="scan-156"><a href="#scan-156"><span class="linenos">156</span></a>            <span class="n">desc</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;brief&quot;</span><span class="p">]</span>
</span><span id="scan-157"><a href="#scan-157"><span class="linenos">157</span></a>            <span class="k">if</span> <span class="s2">&quot;ref&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="scan-158"><a href="#scan-158"><span class="linenos">158</span></a>                <span class="n">refs</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;ref&quot;</span><span class="p">]</span>
</span><span id="scan-159"><a href="#scan-159"><span class="linenos">159</span></a>            <span class="k">if</span> <span class="s2">&quot;test&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">:</span>
</span><span id="scan-160"><a href="#scan-160"><span class="linenos">160</span></a>                <span class="n">tests</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span><span class="p">[</span><span class="s2">&quot;test&quot;</span><span class="p">]</span>
</span><span id="scan-161"><a href="#scan-161"><span class="linenos">161</span></a>        <span class="n">iswater</span><span class="p">[</span><span class="n">mod</span><span class="p">]</span> <span class="o">=</span> <span class="n">_is_water_module</span><span class="p">(</span><span class="n">module</span><span class="p">,</span> <span class="n">category</span><span class="p">)</span>
</span><span id="scan-162"><a href="#scan-162"><span class="linenos">162</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="n">mods</span><span class="p">)</span>
</span><span id="scan-163"><a href="#scan-163"><span class="linenos">163</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;local&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">mods</span>
</span><span id="scan-164"><a href="#scan-164"><span class="linenos">164</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;desc&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">desc</span>
</span><span id="scan-165"><a href="#scan-165"><span class="linenos">165</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;iswater&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">iswater</span>
</span><span id="scan-166"><a href="#scan-166"><span class="linenos">166</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;refs&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">refs</span>
</span><span id="scan-167"><a href="#scan-167"><span class="linenos">167</span></a>    <span class="n">modules</span><span class="p">[</span><span class="s2">&quot;tests&quot;</span><span class="p">]</span> <span class="o">=</span> <span class="n">tests</span>
</span><span id="scan-168"><a href="#scan-168"><span class="linenos">168</span></a>
</span><span id="scan-169"><a href="#scan-169"><span class="linenos">169</span></a>    <span class="k">return</span> <span class="n">modules</span>
</span></pre></div>


            <div class="docstring"><p>Scan available plugins.</p>
</div>


                </section>
                <section id="descriptions">
                            <input id="descriptions-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">descriptions</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">category</span>, </span><span class="param"><span class="n">width</span><span class="o">=</span><span class="mi">72</span>, </span><span class="param"><span class="n">water</span><span class="o">=</span><span class="kc">False</span>, </span><span class="param"><span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s1">&#39;system&#39;</span><span class="p">,</span> <span class="s1">&#39;extra&#39;</span><span class="p">,</span> <span class="s1">&#39;local&#39;</span><span class="p">)</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="descriptions-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#descriptions"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="descriptions-172"><a href="#descriptions-172"><span class="linenos">172</span></a><span class="k">def</span><span class="w"> </span><span class="nf">descriptions</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">width</span><span class="o">=</span><span class="mi">72</span><span class="p">,</span> <span class="n">water</span><span class="o">=</span><span class="kc">False</span><span class="p">,</span> <span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s2">&quot;system&quot;</span><span class="p">,</span> <span class="s2">&quot;extra&quot;</span><span class="p">,</span> <span class="s2">&quot;local&quot;</span><span class="p">)):</span>
</span><span id="descriptions-173"><a href="#descriptions-173"><span class="linenos">173</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="descriptions-174"><a href="#descriptions-174"><span class="linenos">174</span></a><span class="sd">    Show the list of available plugins in the category.</span>
</span><span id="descriptions-175"><a href="#descriptions-175"><span class="linenos">175</span></a>
</span><span id="descriptions-176"><a href="#descriptions-176"><span class="linenos">176</span></a><span class="sd">    Options:</span>
</span><span id="descriptions-177"><a href="#descriptions-177"><span class="linenos">177</span></a><span class="sd">      width=72      Width of the output.</span>
</span><span id="descriptions-178"><a href="#descriptions-178"><span class="linenos">178</span></a><span class="sd">      water=False   Pick up water molecules only (for molecule plugin).</span>
</span><span id="descriptions-179"><a href="#descriptions-179"><span class="linenos">179</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="descriptions-180"><a href="#descriptions-180"><span class="linenos">180</span></a>    <span class="n">titles</span> <span class="o">=</span> <span class="p">{</span>
</span><span id="descriptions-181"><a href="#descriptions-181"><span class="linenos">181</span></a>        <span class="s2">&quot;lattice&quot;</span><span class="p">:</span> <span class="p">{</span>
</span><span id="descriptions-182"><a href="#descriptions-182"><span class="linenos">182</span></a>            <span class="s2">&quot;system&quot;</span><span class="p">:</span> <span class="s2">&quot;1. Lattice structures served with GenIce&quot;</span><span class="p">,</span>
</span><span id="descriptions-183"><a href="#descriptions-183"><span class="linenos">183</span></a>            <span class="s2">&quot;extra&quot;</span><span class="p">:</span> <span class="s2">&quot;2. Lattice structures served by external plugins&quot;</span><span class="p">,</span>
</span><span id="descriptions-184"><a href="#descriptions-184"><span class="linenos">184</span></a>            <span class="s2">&quot;local&quot;</span><span class="p">:</span> <span class="s2">&quot;3. Lattice structures served locally&quot;</span><span class="p">,</span>
</span><span id="descriptions-185"><a href="#descriptions-185"><span class="linenos">185</span></a>            <span class="s2">&quot;title&quot;</span><span class="p">:</span> <span class="s2">&quot;[Available lattice structures]&quot;</span><span class="p">,</span>
</span><span id="descriptions-186"><a href="#descriptions-186"><span class="linenos">186</span></a>        <span class="p">},</span>
</span><span id="descriptions-187"><a href="#descriptions-187"><span class="linenos">187</span></a>        <span class="s2">&quot;format&quot;</span><span class="p">:</span> <span class="p">{</span>
</span><span id="descriptions-188"><a href="#descriptions-188"><span class="linenos">188</span></a>            <span class="s2">&quot;system&quot;</span><span class="p">:</span> <span class="s2">&quot;1. Formatters served with GenIce&quot;</span><span class="p">,</span>
</span><span id="descriptions-189"><a href="#descriptions-189"><span class="linenos">189</span></a>            <span class="s2">&quot;extra&quot;</span><span class="p">:</span> <span class="s2">&quot;2. Formatters served by external plugins&quot;</span><span class="p">,</span>
</span><span id="descriptions-190"><a href="#descriptions-190"><span class="linenos">190</span></a>            <span class="s2">&quot;local&quot;</span><span class="p">:</span> <span class="s2">&quot;3. Formatters served locally&quot;</span><span class="p">,</span>
</span><span id="descriptions-191"><a href="#descriptions-191"><span class="linenos">191</span></a>            <span class="s2">&quot;title&quot;</span><span class="p">:</span> <span class="s2">&quot;[Available formatters]&quot;</span><span class="p">,</span>
</span><span id="descriptions-192"><a href="#descriptions-192"><span class="linenos">192</span></a>        <span class="p">},</span>
</span><span id="descriptions-193"><a href="#descriptions-193"><span class="linenos">193</span></a>        <span class="s2">&quot;loader&quot;</span><span class="p">:</span> <span class="p">{</span>
</span><span id="descriptions-194"><a href="#descriptions-194"><span class="linenos">194</span></a>            <span class="s2">&quot;system&quot;</span><span class="p">:</span> <span class="s2">&quot;1. File types served with GenIce&quot;</span><span class="p">,</span>
</span><span id="descriptions-195"><a href="#descriptions-195"><span class="linenos">195</span></a>            <span class="s2">&quot;extra&quot;</span><span class="p">:</span> <span class="s2">&quot;2. File types served by external eplugins&quot;</span><span class="p">,</span>
</span><span id="descriptions-196"><a href="#descriptions-196"><span class="linenos">196</span></a>            <span class="s2">&quot;local&quot;</span><span class="p">:</span> <span class="s2">&quot;3. File types served locally&quot;</span><span class="p">,</span>
</span><span id="descriptions-197"><a href="#descriptions-197"><span class="linenos">197</span></a>            <span class="s2">&quot;title&quot;</span><span class="p">:</span> <span class="s2">&quot;[Available input file types]&quot;</span><span class="p">,</span>
</span><span id="descriptions-198"><a href="#descriptions-198"><span class="linenos">198</span></a>        <span class="p">},</span>
</span><span id="descriptions-199"><a href="#descriptions-199"><span class="linenos">199</span></a>        <span class="s2">&quot;molecule&quot;</span><span class="p">:</span> <span class="p">{</span>
</span><span id="descriptions-200"><a href="#descriptions-200"><span class="linenos">200</span></a>            <span class="s2">&quot;system&quot;</span><span class="p">:</span> <span class="s2">&quot;1. Molecules served with GenIce&quot;</span><span class="p">,</span>
</span><span id="descriptions-201"><a href="#descriptions-201"><span class="linenos">201</span></a>            <span class="s2">&quot;extra&quot;</span><span class="p">:</span> <span class="s2">&quot;2. Molecules served by external plugins&quot;</span><span class="p">,</span>
</span><span id="descriptions-202"><a href="#descriptions-202"><span class="linenos">202</span></a>            <span class="s2">&quot;local&quot;</span><span class="p">:</span> <span class="s2">&quot;3. Molecules served locally&quot;</span><span class="p">,</span>
</span><span id="descriptions-203"><a href="#descriptions-203"><span class="linenos">203</span></a>            <span class="s2">&quot;title&quot;</span><span class="p">:</span> <span class="s2">&quot;[Available molecules]&quot;</span><span class="p">,</span>
</span><span id="descriptions-204"><a href="#descriptions-204"><span class="linenos">204</span></a>        <span class="p">},</span>
</span><span id="descriptions-205"><a href="#descriptions-205"><span class="linenos">205</span></a>    <span class="p">}</span>
</span><span id="descriptions-206"><a href="#descriptions-206"><span class="linenos">206</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="n">scan</span><span class="p">(</span><span class="n">category</span><span class="p">)</span>
</span><span id="descriptions-207"><a href="#descriptions-207"><span class="linenos">207</span></a>    <span class="n">catalog</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot; </span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="si">{</span><span class="n">titles</span><span class="p">[</span><span class="n">category</span><span class="p">][</span><span class="s1">&#39;title&#39;</span><span class="p">]</span><span class="si">}</span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="descriptions-208"><a href="#descriptions-208"><span class="linenos">208</span></a>    <span class="n">desc</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;desc&quot;</span><span class="p">]</span>
</span><span id="descriptions-209"><a href="#descriptions-209"><span class="linenos">209</span></a>    <span class="n">iswater</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;iswater&quot;</span><span class="p">]</span>
</span><span id="descriptions-210"><a href="#descriptions-210"><span class="linenos">210</span></a>    <span class="k">for</span> <span class="n">group</span> <span class="ow">in</span> <span class="n">groups</span><span class="p">:</span>
</span><span id="descriptions-211"><a href="#descriptions-211"><span class="linenos">211</span></a>        <span class="n">desced</span> <span class="o">=</span> <span class="n">defaultdict</span><span class="p">(</span><span class="nb">list</span><span class="p">)</span>
</span><span id="descriptions-212"><a href="#descriptions-212"><span class="linenos">212</span></a>        <span class="n">undesc</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="descriptions-213"><a href="#descriptions-213"><span class="linenos">213</span></a>        <span class="k">for</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">mods</span><span class="p">[</span><span class="n">group</span><span class="p">]:</span>
</span><span id="descriptions-214"><a href="#descriptions-214"><span class="linenos">214</span></a>            <span class="k">if</span> <span class="n">category</span> <span class="o">==</span> <span class="s2">&quot;molecule&quot;</span><span class="p">:</span>
</span><span id="descriptions-215"><a href="#descriptions-215"><span class="linenos">215</span></a>                <span class="k">if</span> <span class="n">L</span> <span class="ow">not</span> <span class="ow">in</span> <span class="n">iswater</span><span class="p">:</span>
</span><span id="descriptions-216"><a href="#descriptions-216"><span class="linenos">216</span></a>                    <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]</span> <span class="o">=</span> <span class="kc">False</span>
</span><span id="descriptions-217"><a href="#descriptions-217"><span class="linenos">217</span></a>                <span class="k">if</span> <span class="n">water</span> <span class="ow">and</span> <span class="ow">not</span> <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]:</span>
</span><span id="descriptions-218"><a href="#descriptions-218"><span class="linenos">218</span></a>                    <span class="k">continue</span>
</span><span id="descriptions-219"><a href="#descriptions-219"><span class="linenos">219</span></a>                <span class="k">if</span> <span class="ow">not</span> <span class="n">water</span> <span class="ow">and</span> <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]:</span>
</span><span id="descriptions-220"><a href="#descriptions-220"><span class="linenos">220</span></a>                    <span class="k">continue</span>
</span><span id="descriptions-221"><a href="#descriptions-221"><span class="linenos">221</span></a>            <span class="k">if</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">desc</span><span class="p">:</span>
</span><span id="descriptions-222"><a href="#descriptions-222"><span class="linenos">222</span></a>                <span class="n">desced</span><span class="p">[</span><span class="n">desc</span><span class="p">[</span><span class="n">L</span><span class="p">]]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">L</span><span class="p">)</span>
</span><span id="descriptions-223"><a href="#descriptions-223"><span class="linenos">223</span></a>            <span class="k">else</span><span class="p">:</span>
</span><span id="descriptions-224"><a href="#descriptions-224"><span class="linenos">224</span></a>                <span class="n">undesc</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">L</span><span class="p">)</span>
</span><span id="descriptions-225"><a href="#descriptions-225"><span class="linenos">225</span></a>        <span class="k">for</span> <span class="n">dd</span> <span class="ow">in</span> <span class="n">desced</span><span class="p">:</span>
</span><span id="descriptions-226"><a href="#descriptions-226"><span class="linenos">226</span></a>            <span class="n">desced</span><span class="p">[</span><span class="n">dd</span><span class="p">]</span> <span class="o">=</span> <span class="s2">&quot;, &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">desced</span><span class="p">[</span><span class="n">dd</span><span class="p">])</span>
</span><span id="descriptions-227"><a href="#descriptions-227"><span class="linenos">227</span></a>        <span class="n">catalog</span> <span class="o">+=</span> <span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">titles</span><span class="p">[</span><span class="n">category</span><span class="p">][</span><span class="n">group</span><span class="p">]</span><span class="si">}</span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="descriptions-228"><a href="#descriptions-228"><span class="linenos">228</span></a>        <span class="n">table</span> <span class="o">=</span> <span class="s2">&quot;&quot;</span>
</span><span id="descriptions-229"><a href="#descriptions-229"><span class="linenos">229</span></a>        <span class="k">for</span> <span class="n">dd</span> <span class="ow">in</span> <span class="nb">sorted</span><span class="p">(</span><span class="n">desced</span><span class="p">,</span> <span class="n">key</span><span class="o">=</span><span class="k">lambda</span> <span class="n">x</span><span class="p">:</span> <span class="n">desced</span><span class="p">[</span><span class="n">x</span><span class="p">]):</span>
</span><span id="descriptions-230"><a href="#descriptions-230"><span class="linenos">230</span></a>            <span class="n">table</span> <span class="o">+=</span> <span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">desced</span><span class="p">[</span><span class="n">dd</span><span class="p">]</span><span class="si">}</span><span class="se">\t</span><span class="si">{</span><span class="n">dd</span><span class="si">}</span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="descriptions-231"><a href="#descriptions-231"><span class="linenos">231</span></a>        <span class="k">if</span> <span class="n">table</span> <span class="o">==</span> <span class="s2">&quot;&quot;</span><span class="p">:</span>
</span><span id="descriptions-232"><a href="#descriptions-232"><span class="linenos">232</span></a>            <span class="n">table</span> <span class="o">=</span> <span class="s2">&quot;(None)</span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="descriptions-233"><a href="#descriptions-233"><span class="linenos">233</span></a>        <span class="n">table</span> <span class="o">=</span> <span class="p">[</span>
</span><span id="descriptions-234"><a href="#descriptions-234"><span class="linenos">234</span></a>            <span class="n">fill</span><span class="p">(</span>
</span><span id="descriptions-235"><a href="#descriptions-235"><span class="linenos">235</span></a>                <span class="n">line</span><span class="p">,</span>
</span><span id="descriptions-236"><a href="#descriptions-236"><span class="linenos">236</span></a>                <span class="n">width</span><span class="o">=</span><span class="n">width</span><span class="p">,</span>
</span><span id="descriptions-237"><a href="#descriptions-237"><span class="linenos">237</span></a>                <span class="n">drop_whitespace</span><span class="o">=</span><span class="kc">False</span><span class="p">,</span>
</span><span id="descriptions-238"><a href="#descriptions-238"><span class="linenos">238</span></a>                <span class="n">expand_tabs</span><span class="o">=</span><span class="kc">True</span><span class="p">,</span>
</span><span id="descriptions-239"><a href="#descriptions-239"><span class="linenos">239</span></a>                <span class="n">tabsize</span><span class="o">=</span><span class="mi">16</span><span class="p">,</span>
</span><span id="descriptions-240"><a href="#descriptions-240"><span class="linenos">240</span></a>                <span class="n">subsequent_indent</span><span class="o">=</span><span class="s2">&quot; &quot;</span> <span class="o">*</span> <span class="mi">16</span><span class="p">,</span>
</span><span id="descriptions-241"><a href="#descriptions-241"><span class="linenos">241</span></a>            <span class="p">)</span>
</span><span id="descriptions-242"><a href="#descriptions-242"><span class="linenos">242</span></a>            <span class="k">for</span> <span class="n">line</span> <span class="ow">in</span> <span class="n">table</span><span class="o">.</span><span class="n">splitlines</span><span class="p">()</span>
</span><span id="descriptions-243"><a href="#descriptions-243"><span class="linenos">243</span></a>        <span class="p">]</span>
</span><span id="descriptions-244"><a href="#descriptions-244"><span class="linenos">244</span></a>        <span class="n">table</span> <span class="o">=</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">&quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">table</span><span class="p">)</span> <span class="o">+</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="descriptions-245"><a href="#descriptions-245"><span class="linenos">245</span></a>        <span class="n">undesc</span> <span class="o">=</span> <span class="s2">&quot; &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="n">undesc</span><span class="p">)</span>
</span><span id="descriptions-246"><a href="#descriptions-246"><span class="linenos">246</span></a>        <span class="k">if</span> <span class="n">undesc</span> <span class="o">!=</span> <span class="s2">&quot;&quot;</span><span class="p">:</span>
</span><span id="descriptions-247"><a href="#descriptions-247"><span class="linenos">247</span></a>            <span class="n">undesc</span> <span class="o">=</span> <span class="s2">&quot;(Undocumented) &quot;</span> <span class="o">+</span> <span class="n">undesc</span>
</span><span id="descriptions-248"><a href="#descriptions-248"><span class="linenos">248</span></a>        <span class="n">catalog</span> <span class="o">+=</span> <span class="n">table</span> <span class="o">+</span> <span class="s2">&quot;----</span><span class="se">\n</span><span class="s2">&quot;</span> <span class="o">+</span> <span class="n">undesc</span> <span class="o">+</span> <span class="s2">&quot;</span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="s2"> </span><span class="se">\n</span><span class="s2">&quot;</span>
</span><span id="descriptions-249"><a href="#descriptions-249"><span class="linenos">249</span></a>    <span class="k">return</span> <span class="n">catalog</span>
</span></pre></div>


            <div class="docstring"><p>Show the list of available plugins in the category.</p>

<p>Options:
  width=72      Width of the output.
  water=False   Pick up water molecules only (for molecule plugin).</p>
</div>


                </section>
                <section id="plugin_descriptors">
                            <input id="plugin_descriptors-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">plugin_descriptors</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">category</span>, </span><span class="param"><span class="n">water</span><span class="o">=</span><span class="kc">False</span>, </span><span class="param"><span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s1">&#39;system&#39;</span><span class="p">,</span> <span class="s1">&#39;extra&#39;</span><span class="p">,</span> <span class="s1">&#39;local&#39;</span><span class="p">)</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="plugin_descriptors-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#plugin_descriptors"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="plugin_descriptors-252"><a href="#plugin_descriptors-252"><span class="linenos">252</span></a><span class="k">def</span><span class="w"> </span><span class="nf">plugin_descriptors</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">water</span><span class="o">=</span><span class="kc">False</span><span class="p">,</span> <span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s2">&quot;system&quot;</span><span class="p">,</span> <span class="s2">&quot;extra&quot;</span><span class="p">,</span> <span class="s2">&quot;local&quot;</span><span class="p">)):</span>
</span><span id="plugin_descriptors-253"><a href="#plugin_descriptors-253"><span class="linenos">253</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="plugin_descriptors-254"><a href="#plugin_descriptors-254"><span class="linenos">254</span></a><span class="sd">    Show the list of available plugins in the category.</span>
</span><span id="plugin_descriptors-255"><a href="#plugin_descriptors-255"><span class="linenos">255</span></a>
</span><span id="plugin_descriptors-256"><a href="#plugin_descriptors-256"><span class="linenos">256</span></a><span class="sd">    Options:</span>
</span><span id="plugin_descriptors-257"><a href="#plugin_descriptors-257"><span class="linenos">257</span></a><span class="sd">      water=False   Pick up water molecules only (for molecule plugin).</span>
</span><span id="plugin_descriptors-258"><a href="#plugin_descriptors-258"><span class="linenos">258</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="plugin_descriptors-259"><a href="#plugin_descriptors-259"><span class="linenos">259</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="n">scan</span><span class="p">(</span><span class="n">category</span><span class="p">)</span>
</span><span id="plugin_descriptors-260"><a href="#plugin_descriptors-260"><span class="linenos">260</span></a>    <span class="n">catalog</span> <span class="o">=</span> <span class="nb">dict</span><span class="p">()</span>
</span><span id="plugin_descriptors-261"><a href="#plugin_descriptors-261"><span class="linenos">261</span></a>    <span class="n">desc</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;desc&quot;</span><span class="p">]</span>
</span><span id="plugin_descriptors-262"><a href="#plugin_descriptors-262"><span class="linenos">262</span></a>    <span class="n">iswater</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;iswater&quot;</span><span class="p">]</span>
</span><span id="plugin_descriptors-263"><a href="#plugin_descriptors-263"><span class="linenos">263</span></a>    <span class="n">refs</span> <span class="o">=</span> <span class="n">mods</span><span class="p">[</span><span class="s2">&quot;refs&quot;</span><span class="p">]</span>
</span><span id="plugin_descriptors-264"><a href="#plugin_descriptors-264"><span class="linenos">264</span></a>    <span class="k">for</span> <span class="n">group</span> <span class="ow">in</span> <span class="n">groups</span><span class="p">:</span>
</span><span id="plugin_descriptors-265"><a href="#plugin_descriptors-265"><span class="linenos">265</span></a>        <span class="n">desced</span> <span class="o">=</span> <span class="n">defaultdict</span><span class="p">(</span><span class="nb">list</span><span class="p">)</span>
</span><span id="plugin_descriptors-266"><a href="#plugin_descriptors-266"><span class="linenos">266</span></a>        <span class="n">undesc</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="plugin_descriptors-267"><a href="#plugin_descriptors-267"><span class="linenos">267</span></a>        <span class="n">refss</span> <span class="o">=</span> <span class="n">defaultdict</span><span class="p">(</span><span class="nb">set</span><span class="p">)</span>
</span><span id="plugin_descriptors-268"><a href="#plugin_descriptors-268"><span class="linenos">268</span></a>        <span class="k">for</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">mods</span><span class="p">[</span><span class="n">group</span><span class="p">]:</span>
</span><span id="plugin_descriptors-269"><a href="#plugin_descriptors-269"><span class="linenos">269</span></a>            <span class="k">if</span> <span class="n">category</span> <span class="o">==</span> <span class="s2">&quot;molecule&quot;</span><span class="p">:</span>
</span><span id="plugin_descriptors-270"><a href="#plugin_descriptors-270"><span class="linenos">270</span></a>                <span class="k">if</span> <span class="n">L</span> <span class="ow">not</span> <span class="ow">in</span> <span class="n">iswater</span><span class="p">:</span>
</span><span id="plugin_descriptors-271"><a href="#plugin_descriptors-271"><span class="linenos">271</span></a>                    <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]</span> <span class="o">=</span> <span class="kc">False</span>
</span><span id="plugin_descriptors-272"><a href="#plugin_descriptors-272"><span class="linenos">272</span></a>                <span class="k">if</span> <span class="n">water</span> <span class="ow">and</span> <span class="ow">not</span> <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]:</span>
</span><span id="plugin_descriptors-273"><a href="#plugin_descriptors-273"><span class="linenos">273</span></a>                    <span class="k">continue</span>
</span><span id="plugin_descriptors-274"><a href="#plugin_descriptors-274"><span class="linenos">274</span></a>                <span class="k">if</span> <span class="ow">not</span> <span class="n">water</span> <span class="ow">and</span> <span class="n">iswater</span><span class="p">[</span><span class="n">L</span><span class="p">]:</span>
</span><span id="plugin_descriptors-275"><a href="#plugin_descriptors-275"><span class="linenos">275</span></a>                    <span class="k">continue</span>
</span><span id="plugin_descriptors-276"><a href="#plugin_descriptors-276"><span class="linenos">276</span></a>            <span class="k">if</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">desc</span><span class="p">:</span>
</span><span id="plugin_descriptors-277"><a href="#plugin_descriptors-277"><span class="linenos">277</span></a>                <span class="c1"># desc[L] is the brief description of the module</span>
</span><span id="plugin_descriptors-278"><a href="#plugin_descriptors-278"><span class="linenos">278</span></a>                <span class="c1"># L is the name of module (name of ice)</span>
</span><span id="plugin_descriptors-279"><a href="#plugin_descriptors-279"><span class="linenos">279</span></a>                <span class="n">desced</span><span class="p">[</span><span class="n">desc</span><span class="p">[</span><span class="n">L</span><span class="p">]]</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">L</span><span class="p">)</span>
</span><span id="plugin_descriptors-280"><a href="#plugin_descriptors-280"><span class="linenos">280</span></a>                <span class="k">if</span> <span class="n">L</span> <span class="ow">in</span> <span class="n">refs</span><span class="p">:</span>
</span><span id="plugin_descriptors-281"><a href="#plugin_descriptors-281"><span class="linenos">281</span></a>                    <span class="n">refss</span><span class="p">[</span><span class="n">desc</span><span class="p">[</span><span class="n">L</span><span class="p">]]</span> <span class="o">|=</span> <span class="nb">set</span><span class="p">([</span><span class="n">label</span> <span class="k">for</span> <span class="n">key</span><span class="p">,</span> <span class="n">label</span> <span class="ow">in</span> <span class="n">refs</span><span class="p">[</span><span class="n">L</span><span class="p">]</span><span class="o">.</span><span class="n">items</span><span class="p">()])</span>
</span><span id="plugin_descriptors-282"><a href="#plugin_descriptors-282"><span class="linenos">282</span></a>            <span class="k">else</span><span class="p">:</span>
</span><span id="plugin_descriptors-283"><a href="#plugin_descriptors-283"><span class="linenos">283</span></a>                <span class="n">undesc</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">L</span><span class="p">)</span>
</span><span id="plugin_descriptors-284"><a href="#plugin_descriptors-284"><span class="linenos">284</span></a>        <span class="n">catalog</span><span class="p">[</span><span class="n">group</span><span class="p">]</span> <span class="o">=</span> <span class="p">[</span><span class="n">desced</span><span class="p">,</span> <span class="n">undesc</span><span class="p">,</span> <span class="n">refss</span><span class="p">]</span>
</span><span id="plugin_descriptors-285"><a href="#plugin_descriptors-285"><span class="linenos">285</span></a>    <span class="k">return</span> <span class="n">catalog</span>
</span></pre></div>


            <div class="docstring"><p>Show the list of available plugins in the category.</p>

<p>Options:
  water=False   Pick up water molecules only (for molecule plugin).</p>
</div>


                </section>
                <section id="audit_name">
                            <input id="audit_name-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">audit_name</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">name</span><span class="p">:</span> <span class="nb">str</span>, </span><span class="param"><span class="n">category</span><span class="p">:</span> <span class="nb">str</span> <span class="o">=</span> <span class="s1">&#39;plugin&#39;</span></span><span class="return-annotation">) -> <span class="nb">str</span>:</span></span>

                <label class="view-source-button" for="audit_name-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#audit_name"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="audit_name-288"><a href="#audit_name-288"><span class="linenos">288</span></a><span class="k">def</span><span class="w"> </span><span class="nf">audit_name</span><span class="p">(</span><span class="n">name</span><span class="p">:</span> <span class="nb">str</span><span class="p">,</span> <span class="n">category</span><span class="p">:</span> <span class="nb">str</span> <span class="o">=</span> <span class="s2">&quot;plugin&quot;</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="nb">str</span><span class="p">:</span>
</span><span id="audit_name-289"><a href="#audit_name-289"><span class="linenos">289</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="audit_name-290"><a href="#audit_name-290"><span class="linenos">290</span></a><span class="sd">    Audit the mol name to avoid the access to unexpected files</span>
</span><span id="audit_name-291"><a href="#audit_name-291"><span class="linenos">291</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="audit_name-292"><a href="#audit_name-292"><span class="linenos">292</span></a>    <span class="n">match</span> <span class="o">=</span> <span class="n">re</span><span class="o">.</span><span class="n">match</span><span class="p">(</span><span class="s2">&quot;^[A-Za-z0-9-_]+$&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span>
</span><span id="audit_name-293"><a href="#audit_name-293"><span class="linenos">293</span></a>    <span class="k">if</span> <span class="n">match</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="audit_name-294"><a href="#audit_name-294"><span class="linenos">294</span></a>        <span class="k">return</span> <span class="n">name</span>
</span><span id="audit_name-295"><a href="#audit_name-295"><span class="linenos">295</span></a>    <span class="n">match</span> <span class="o">=</span> <span class="n">re</span><span class="o">.</span><span class="n">match</span><span class="p">(</span><span class="sa">r</span><span class="s2">&quot;^\[([A-Za-z0-9-_]+) .*\]$&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span>
</span><span id="audit_name-296"><a href="#audit_name-296"><span class="linenos">296</span></a>    <span class="k">if</span> <span class="n">match</span> <span class="ow">is</span> <span class="ow">not</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="audit_name-297"><a href="#audit_name-297"><span class="linenos">297</span></a>        <span class="k">return</span> <span class="n">match</span><span class="o">.</span><span class="n">group</span><span class="p">(</span><span class="mi">1</span><span class="p">)</span>
</span><span id="audit_name-298"><a href="#audit_name-298"><span class="linenos">298</span></a>    <span class="k">raise</span> <span class="ne">ValueError</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Dubious </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2"> name: </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span></pre></div>


            <div class="docstring"><p>Audit the mol name to avoid the access to unexpected files</p>
</div>


                </section>
                <section id="import_extra">
                            <input id="import_extra-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">import_extra</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">category</span>, </span><span class="param"><span class="n">name</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="import_extra-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#import_extra"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="import_extra-301"><a href="#import_extra-301"><span class="linenos">301</span></a><span class="k">def</span><span class="w"> </span><span class="nf">import_extra</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">name</span><span class="p">):</span>
</span><span id="import_extra-302"><a href="#import_extra-302"><span class="linenos">302</span></a>    <span class="n">logger</span> <span class="o">=</span> <span class="n">getLogger</span><span class="p">()</span>
</span><span id="import_extra-303"><a href="#import_extra-303"><span class="linenos">303</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Extra </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2"> plugin: </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="import_extra-304"><a href="#import_extra-304"><span class="linenos">304</span></a>    <span class="n">groupname</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot;genice3_</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="import_extra-305"><a href="#import_extra-305"><span class="linenos">305</span></a>    <span class="n">module</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="import_extra-306"><a href="#import_extra-306"><span class="linenos">306</span></a>    <span class="c1"># for ep in pr.iter_entry_points(group=groupname):</span>
</span><span id="import_extra-307"><a href="#import_extra-307"><span class="linenos">307</span></a>    <span class="k">for</span> <span class="n">ep</span> <span class="ow">in</span> <span class="n">entry_points</span><span class="p">(</span><span class="n">group</span><span class="o">=</span><span class="n">groupname</span><span class="p">):</span>
</span><span id="import_extra-308"><a href="#import_extra-308"><span class="linenos">308</span></a>        <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;    Entry point: </span><span class="si">{</span><span class="n">ep</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="import_extra-309"><a href="#import_extra-309"><span class="linenos">309</span></a>        <span class="k">if</span> <span class="n">ep</span><span class="o">.</span><span class="n">name</span> <span class="o">==</span> <span class="n">name</span><span class="p">:</span>
</span><span id="import_extra-310"><a href="#import_extra-310"><span class="linenos">310</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;      Loading </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">...&quot;</span><span class="p">)</span>
</span><span id="import_extra-311"><a href="#import_extra-311"><span class="linenos">311</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">ep</span><span class="o">.</span><span class="n">load</span><span class="p">()</span>
</span><span id="import_extra-312"><a href="#import_extra-312"><span class="linenos">312</span></a>    <span class="k">if</span> <span class="n">module</span> <span class="ow">is</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="import_extra-313"><a href="#import_extra-313"><span class="linenos">313</span></a>        <span class="k">raise</span> <span class="ne">ImportError</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Nonexistent or failed to load the </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2"> module: </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="import_extra-314"><a href="#import_extra-314"><span class="linenos">314</span></a>    <span class="k">return</span> <span class="n">module</span>
</span></pre></div>


    

                </section>
                <section id="safe_import">
                            <input id="safe_import-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">safe_import</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">category</span>, </span><span class="param"><span class="n">name</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="safe_import-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#safe_import"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="safe_import-317"><a href="#safe_import-317"><span class="linenos">317</span></a><span class="k">def</span><span class="w"> </span><span class="nf">safe_import</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">name</span><span class="p">):</span>
</span><span id="safe_import-318"><a href="#safe_import-318"><span class="linenos">318</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="safe_import-319"><a href="#safe_import-319"><span class="linenos">319</span></a><span class="sd">    Load a plugin.</span>
</span><span id="safe_import-320"><a href="#safe_import-320"><span class="linenos">320</span></a>
</span><span id="safe_import-321"><a href="#safe_import-321"><span class="linenos">321</span></a><span class="sd">    The plugins can exist either in the system, as a extra plugin, or in the</span>
</span><span id="safe_import-322"><a href="#safe_import-322"><span class="linenos">322</span></a><span class="sd">    local folder.</span>
</span><span id="safe_import-323"><a href="#safe_import-323"><span class="linenos">323</span></a>
</span><span id="safe_import-324"><a href="#safe_import-324"><span class="linenos">324</span></a><span class="sd">    category: The type of the plugin; &quot;lattice&quot;, &quot;format&quot;, &quot;molecule&quot;, or &quot;loader&quot;.</span>
</span><span id="safe_import-325"><a href="#safe_import-325"><span class="linenos">325</span></a><span class="sd">    name:     The name of the plugin.</span>
</span><span id="safe_import-326"><a href="#safe_import-326"><span class="linenos">326</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="safe_import-327"><a href="#safe_import-327"><span class="linenos">327</span></a>    <span class="n">logger</span> <span class="o">=</span> <span class="n">getLogger</span><span class="p">()</span>
</span><span id="safe_import-328"><a href="#safe_import-328"><span class="linenos">328</span></a>    <span class="k">if</span> <span class="n">category</span> <span class="ow">not</span> <span class="ow">in</span> <span class="p">(</span><span class="s2">&quot;exporter&quot;</span><span class="p">,</span> <span class="s2">&quot;molecule&quot;</span><span class="p">,</span> <span class="s2">&quot;unitcell&quot;</span><span class="p">,</span> <span class="s2">&quot;group&quot;</span><span class="p">):</span>
</span><span id="safe_import-329"><a href="#safe_import-329"><span class="linenos">329</span></a>        <span class="k">raise</span> <span class="ne">ValueError</span><span class="p">(</span>
</span><span id="safe_import-330"><a href="#safe_import-330"><span class="linenos">330</span></a>            <span class="sa">f</span><span class="s2">&quot;category must be &#39;exporter&#39;, &#39;molecule&#39;, &#39;unitcell&#39;, or &#39;group&#39;, got: </span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="safe_import-331"><a href="#safe_import-331"><span class="linenos">331</span></a>        <span class="p">)</span>
</span><span id="safe_import-332"><a href="#safe_import-332"><span class="linenos">332</span></a>
</span><span id="safe_import-333"><a href="#safe_import-333"><span class="linenos">333</span></a>    <span class="c1"># single ? as a plugin name ==&gt; show descriptions (list all)</span>
</span><span id="safe_import-334"><a href="#safe_import-334"><span class="linenos">334</span></a>    <span class="k">if</span> <span class="n">name</span> <span class="o">==</span> <span class="s2">&quot;?&quot;</span><span class="p">:</span>
</span><span id="safe_import-335"><a href="#safe_import-335"><span class="linenos">335</span></a>        <span class="nb">print</span><span class="p">(</span><span class="n">descriptions</span><span class="p">(</span><span class="n">category</span><span class="p">))</span>
</span><span id="safe_import-336"><a href="#safe_import-336"><span class="linenos">336</span></a>        <span class="n">sys</span><span class="o">.</span><span class="n">exit</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span>
</span><span id="safe_import-337"><a href="#safe_import-337"><span class="linenos">337</span></a>
</span><span id="safe_import-338"><a href="#safe_import-338"><span class="linenos">338</span></a>    <span class="c1"># SYMBOL? ==&gt; show usage for that plugin (then exit)</span>
</span><span id="safe_import-339"><a href="#safe_import-339"><span class="linenos">339</span></a>    <span class="n">usage</span> <span class="o">=</span> <span class="kc">False</span>
</span><span id="safe_import-340"><a href="#safe_import-340"><span class="linenos">340</span></a>    <span class="k">if</span> <span class="nb">len</span><span class="p">(</span><span class="n">name</span><span class="p">)</span> <span class="o">&gt;</span> <span class="mi">1</span> <span class="ow">and</span> <span class="n">name</span><span class="p">[</span><span class="o">-</span><span class="mi">1</span><span class="p">]</span> <span class="o">==</span> <span class="s2">&quot;?&quot;</span><span class="p">:</span>
</span><span id="safe_import-341"><a href="#safe_import-341"><span class="linenos">341</span></a>        <span class="n">usage</span> <span class="o">=</span> <span class="kc">True</span>
</span><span id="safe_import-342"><a href="#safe_import-342"><span class="linenos">342</span></a>        <span class="n">name</span> <span class="o">=</span> <span class="n">name</span><span class="p">[:</span><span class="o">-</span><span class="mi">1</span><span class="p">]</span>
</span><span id="safe_import-343"><a href="#safe_import-343"><span class="linenos">343</span></a>
</span><span id="safe_import-344"><a href="#safe_import-344"><span class="linenos">344</span></a>    <span class="n">module_name</span> <span class="o">=</span> <span class="n">audit_name</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="n">category</span><span class="p">)</span>
</span><span id="safe_import-345"><a href="#safe_import-345"><span class="linenos">345</span></a>
</span><span id="safe_import-346"><a href="#safe_import-346"><span class="linenos">346</span></a>    <span class="n">module</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="safe_import-347"><a href="#safe_import-347"><span class="linenos">347</span></a>    <span class="n">fullname</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">module_name</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="safe_import-348"><a href="#safe_import-348"><span class="linenos">348</span></a>    <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Try to Load a local module: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="safe_import-349"><a href="#safe_import-349"><span class="linenos">349</span></a>    <span class="c1"># まずカレントディレクトリを path に挿入して試す（実行ディレクトリの group/ 等を読むため）</span>
</span><span id="safe_import-350"><a href="#safe_import-350"><span class="linenos">350</span></a>    <span class="n">cwd</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">getcwd</span><span class="p">()</span>
</span><span id="safe_import-351"><a href="#safe_import-351"><span class="linenos">351</span></a>    <span class="n">path_inserted</span> <span class="o">=</span> <span class="n">cwd</span> <span class="ow">not</span> <span class="ow">in</span> <span class="n">sys</span><span class="o">.</span><span class="n">path</span>
</span><span id="safe_import-352"><a href="#safe_import-352"><span class="linenos">352</span></a>    <span class="k">if</span> <span class="n">path_inserted</span><span class="p">:</span>
</span><span id="safe_import-353"><a href="#safe_import-353"><span class="linenos">353</span></a>        <span class="n">sys</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">insert</span><span class="p">(</span><span class="mi">0</span><span class="p">,</span> <span class="n">cwd</span><span class="p">)</span>
</span><span id="safe_import-354"><a href="#safe_import-354"><span class="linenos">354</span></a>    <span class="k">try</span><span class="p">:</span>
</span><span id="safe_import-355"><a href="#safe_import-355"><span class="linenos">355</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="safe_import-356"><a href="#safe_import-356"><span class="linenos">356</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="n">fullname</span><span class="p">)</span>
</span><span id="safe_import-357"><a href="#safe_import-357"><span class="linenos">357</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="s2">&quot;Succeeded (local from cwd or path).&quot;</span><span class="p">)</span>
</span><span id="safe_import-358"><a href="#safe_import-358"><span class="linenos">358</span></a>        <span class="k">except</span> <span class="ne">ModuleNotFoundError</span><span class="p">:</span>
</span><span id="safe_import-359"><a href="#safe_import-359"><span class="linenos">359</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Module not found: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="safe_import-360"><a href="#safe_import-360"><span class="linenos">360</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="safe_import-361"><a href="#safe_import-361"><span class="linenos">361</span></a>        <span class="k">except</span> <span class="ne">ImportError</span> <span class="k">as</span> <span class="n">e</span><span class="p">:</span>
</span><span id="safe_import-362"><a href="#safe_import-362"><span class="linenos">362</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">error</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Error importing module </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">: </span><span class="si">{</span><span class="nb">str</span><span class="p">(</span><span class="n">e</span><span class="p">)</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="safe_import-363"><a href="#safe_import-363"><span class="linenos">363</span></a>            <span class="k">raise</span>
</span><span id="safe_import-364"><a href="#safe_import-364"><span class="linenos">364</span></a>    <span class="k">finally</span><span class="p">:</span>
</span><span id="safe_import-365"><a href="#safe_import-365"><span class="linenos">365</span></a>        <span class="k">if</span> <span class="n">path_inserted</span> <span class="ow">and</span> <span class="n">sys</span><span class="o">.</span><span class="n">path</span> <span class="ow">and</span> <span class="n">sys</span><span class="o">.</span><span class="n">path</span><span class="p">[</span><span class="mi">0</span><span class="p">]</span> <span class="o">==</span> <span class="n">cwd</span><span class="p">:</span>
</span><span id="safe_import-366"><a href="#safe_import-366"><span class="linenos">366</span></a>            <span class="n">sys</span><span class="o">.</span><span class="n">path</span><span class="o">.</span><span class="n">pop</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span>
</span><span id="safe_import-367"><a href="#safe_import-367"><span class="linenos">367</span></a>    <span class="k">if</span> <span class="n">module</span> <span class="ow">is</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="safe_import-368"><a href="#safe_import-368"><span class="linenos">368</span></a>        <span class="n">fullname</span> <span class="o">=</span> <span class="sa">f</span><span class="s2">&quot;genice3.</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">module_name</span><span class="si">}</span><span class="s2">&quot;</span>
</span><span id="safe_import-369"><a href="#safe_import-369"><span class="linenos">369</span></a>        <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Try to load a system module: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="safe_import-370"><a href="#safe_import-370"><span class="linenos">370</span></a>        <span class="k">try</span><span class="p">:</span>
</span><span id="safe_import-371"><a href="#safe_import-371"><span class="linenos">371</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="n">fullname</span><span class="p">)</span>
</span><span id="safe_import-372"><a href="#safe_import-372"><span class="linenos">372</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="s2">&quot;Succeeded.&quot;</span><span class="p">)</span>
</span><span id="safe_import-373"><a href="#safe_import-373"><span class="linenos">373</span></a>        <span class="k">except</span> <span class="ne">ModuleNotFoundError</span><span class="p">:</span>
</span><span id="safe_import-374"><a href="#safe_import-374"><span class="linenos">374</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Module not found: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="safe_import-375"><a href="#safe_import-375"><span class="linenos">375</span></a>            <span class="n">module</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="safe_import-376"><a href="#safe_import-376"><span class="linenos">376</span></a>        <span class="k">except</span> <span class="ne">ImportError</span> <span class="k">as</span> <span class="n">e</span><span class="p">:</span>
</span><span id="safe_import-377"><a href="#safe_import-377"><span class="linenos">377</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">error</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Error importing module </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">: </span><span class="si">{</span><span class="nb">str</span><span class="p">(</span><span class="n">e</span><span class="p">)</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="safe_import-378"><a href="#safe_import-378"><span class="linenos">378</span></a>            <span class="k">raise</span>
</span><span id="safe_import-379"><a href="#safe_import-379"><span class="linenos">379</span></a>    <span class="k">if</span> <span class="n">module</span> <span class="ow">is</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="safe_import-380"><a href="#safe_import-380"><span class="linenos">380</span></a>        <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Try to load an extra module: </span><span class="si">{</span><span class="n">fullname</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="safe_import-381"><a href="#safe_import-381"><span class="linenos">381</span></a>        <span class="n">module</span> <span class="o">=</span> <span class="n">import_extra</span><span class="p">(</span><span class="n">category</span><span class="p">,</span> <span class="n">module_name</span><span class="p">)</span>
</span><span id="safe_import-382"><a href="#safe_import-382"><span class="linenos">382</span></a>        <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="s2">&quot;Succeeded.&quot;</span><span class="p">)</span>
</span><span id="safe_import-383"><a href="#safe_import-383"><span class="linenos">383</span></a>
</span><span id="safe_import-384"><a href="#safe_import-384"><span class="linenos">384</span></a>    <span class="k">if</span> <span class="n">usage</span><span class="p">:</span>
</span><span id="safe_import-385"><a href="#safe_import-385"><span class="linenos">385</span></a>        <span class="k">if</span> <span class="s2">&quot;desc&quot;</span> <span class="ow">in</span> <span class="n">module</span><span class="o">.</span><span class="vm">__dict__</span><span class="p">:</span>
</span><span id="safe_import-386"><a href="#safe_import-386"><span class="linenos">386</span></a>            <span class="n">d</span> <span class="o">=</span> <span class="n">module</span><span class="o">.</span><span class="n">desc</span>
</span><span id="safe_import-387"><a href="#safe_import-387"><span class="linenos">387</span></a>            <span class="n">logger</span><span class="o">.</span><span class="n">info</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Usage for &#39;</span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&#39; plugin&quot;</span><span class="p">)</span>
</span><span id="safe_import-388"><a href="#safe_import-388"><span class="linenos">388</span></a>            <span class="k">if</span> <span class="n">category</span> <span class="o">==</span> <span class="s2">&quot;unitcell&quot;</span> <span class="ow">and</span> <span class="n">d</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;options&quot;</span><span class="p">):</span>
</span><span id="safe_import-389"><a href="#safe_import-389"><span class="linenos">389</span></a>                <span class="n">u</span> <span class="o">=</span> <span class="n">format_unitcell_usage</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="n">d</span><span class="p">[</span><span class="s2">&quot;options&quot;</span><span class="p">])</span>
</span><span id="safe_import-390"><a href="#safe_import-390"><span class="linenos">390</span></a>                <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;CLI:  &quot;</span><span class="p">,</span> <span class="n">u</span><span class="p">[</span><span class="s2">&quot;cli&quot;</span><span class="p">])</span>
</span><span id="safe_import-391"><a href="#safe_import-391"><span class="linenos">391</span></a>                <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;API:  &quot;</span><span class="p">,</span> <span class="n">u</span><span class="p">[</span><span class="s2">&quot;api&quot;</span><span class="p">])</span>
</span><span id="safe_import-392"><a href="#safe_import-392"><span class="linenos">392</span></a>                <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;YAML:</span><span class="se">\n</span><span class="s2">&quot;</span><span class="p">,</span> <span class="n">u</span><span class="p">[</span><span class="s2">&quot;yaml&quot;</span><span class="p">])</span>
</span><span id="safe_import-393"><a href="#safe_import-393"><span class="linenos">393</span></a>            <span class="k">elif</span> <span class="n">d</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;usage&quot;</span><span class="p">):</span>
</span><span id="safe_import-394"><a href="#safe_import-394"><span class="linenos">394</span></a>                <span class="nb">print</span><span class="p">(</span><span class="n">d</span><span class="p">[</span><span class="s2">&quot;usage&quot;</span><span class="p">])</span>
</span><span id="safe_import-395"><a href="#safe_import-395"><span class="linenos">395</span></a>            <span class="k">else</span><span class="p">:</span>
</span><span id="safe_import-396"><a href="#safe_import-396"><span class="linenos">396</span></a>                <span class="nb">print</span><span class="p">(</span><span class="s2">&quot;(no usage)&quot;</span><span class="p">)</span>
</span><span id="safe_import-397"><a href="#safe_import-397"><span class="linenos">397</span></a>            <span class="n">sys</span><span class="o">.</span><span class="n">exit</span><span class="p">(</span><span class="mi">0</span><span class="p">)</span>
</span><span id="safe_import-398"><a href="#safe_import-398"><span class="linenos">398</span></a>
</span><span id="safe_import-399"><a href="#safe_import-399"><span class="linenos">399</span></a>    <span class="k">return</span> <span class="n">module</span>
</span></pre></div>


            <div class="docstring"><p>Load a plugin.</p>

<p>The plugins can exist either in the system, as a extra plugin, or in the
local folder.</p>

<p>category: The type of the plugin; "lattice", "format", "molecule", or "loader".
name:     The name of the plugin.</p>
</div>


                </section>
                <section id="UnitCell">
                            <input id="UnitCell-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">UnitCell</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">name</span>, </span><span class="param"><span class="o">**</span><span class="n">kwargs</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="UnitCell-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#UnitCell"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="UnitCell-402"><a href="#UnitCell-402"><span class="linenos">402</span></a><span class="k">def</span><span class="w"> </span><span class="nf">UnitCell</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
</span><span id="UnitCell-403"><a href="#UnitCell-403"><span class="linenos">403</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="UnitCell-404"><a href="#UnitCell-404"><span class="linenos">404</span></a><span class="sd">    Shortcut for safe_import.</span>
</span><span id="UnitCell-405"><a href="#UnitCell-405"><span class="linenos">405</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="UnitCell-406"><a href="#UnitCell-406"><span class="linenos">406</span></a>    <span class="k">return</span> <span class="n">safe_import</span><span class="p">(</span><span class="s2">&quot;unitcell&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span><span class="o">.</span><span class="n">UnitCell</span><span class="p">(</span><span class="o">**</span><span class="n">kwargs</span><span class="p">)</span>
</span></pre></div>


            <div class="docstring"><p>Shortcut for safe_import.</p>
</div>


                </section>
                <section id="Molecule">
                            <input id="Molecule-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">Molecule</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">name</span>, </span><span class="param"><span class="o">**</span><span class="n">kwargs</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="Molecule-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#Molecule"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="Molecule-409"><a href="#Molecule-409"><span class="linenos">409</span></a><span class="k">def</span><span class="w"> </span><span class="nf">Molecule</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
</span><span id="Molecule-410"><a href="#Molecule-410"><span class="linenos">410</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="Molecule-411"><a href="#Molecule-411"><span class="linenos">411</span></a><span class="sd">    Shortcut for safe_import.</span>
</span><span id="Molecule-412"><a href="#Molecule-412"><span class="linenos">412</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="Molecule-413"><a href="#Molecule-413"><span class="linenos">413</span></a>    <span class="k">return</span> <span class="n">safe_import</span><span class="p">(</span><span class="s2">&quot;molecule&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span><span class="o">.</span><span class="n">Molecule</span><span class="p">(</span><span class="o">**</span><span class="n">kwargs</span><span class="p">)</span>
</span></pre></div>


            <div class="docstring"><p>Shortcut for safe_import.</p>
</div>


                </section>
                <section id="Exporter">
                            <input id="Exporter-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">Exporter</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">name</span>, </span><span class="param"><span class="o">**</span><span class="n">kwargs</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="Exporter-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#Exporter"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="Exporter-416"><a href="#Exporter-416"><span class="linenos">416</span></a><span class="k">def</span><span class="w"> </span><span class="nf">Exporter</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
</span><span id="Exporter-417"><a href="#Exporter-417"><span class="linenos">417</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="Exporter-418"><a href="#Exporter-418"><span class="linenos">418</span></a><span class="sd">    Shortcut for safe_import.</span>
</span><span id="Exporter-419"><a href="#Exporter-419"><span class="linenos">419</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="Exporter-420"><a href="#Exporter-420"><span class="linenos">420</span></a>    <span class="k">return</span> <span class="n">safe_import</span><span class="p">(</span><span class="s2">&quot;exporter&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span>
</span></pre></div>


            <div class="docstring"><p>Shortcut for safe_import.</p>
</div>


                </section>
                <section id="Group">
                            <input id="Group-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">Group</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">name</span>, </span><span class="param"><span class="o">**</span><span class="n">kwargs</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="Group-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#Group"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="Group-423"><a href="#Group-423"><span class="linenos">423</span></a><span class="k">def</span><span class="w"> </span><span class="nf">Group</span><span class="p">(</span><span class="n">name</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
</span><span id="Group-424"><a href="#Group-424"><span class="linenos">424</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="Group-425"><a href="#Group-425"><span class="linenos">425</span></a><span class="sd">    Shortcut for safe_import.</span>
</span><span id="Group-426"><a href="#Group-426"><span class="linenos">426</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="Group-427"><a href="#Group-427"><span class="linenos">427</span></a>    <span class="k">return</span> <span class="n">safe_import</span><span class="p">(</span><span class="s2">&quot;group&quot;</span><span class="p">,</span> <span class="n">name</span><span class="p">)</span><span class="o">.</span><span class="n">Group</span><span class="p">(</span><span class="o">**</span><span class="n">kwargs</span><span class="p">)</span>
</span></pre></div>


            <div class="docstring"><p>Shortcut for safe_import.</p>
</div>


                </section>
                <section id="get_exporter_format_rows">
                            <input id="get_exporter_format_rows-view-source" class="view-source-toggle-state" type="checkbox" aria-hidden="true" tabindex="-1">
<div class="attr function">
            
        <span class="def">def</span>
        <span class="name">get_exporter_format_rows</span><span class="signature pdoc-code condensed">(<span class="param"><span class="n">category</span><span class="o">=</span><span class="s1">&#39;exporter&#39;</span>, </span><span class="param"><span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s1">&#39;system&#39;</span><span class="p">,</span> <span class="s1">&#39;extra&#39;</span><span class="p">,</span> <span class="s1">&#39;local&#39;</span><span class="p">)</span></span><span class="return-annotation">):</span></span>

                <label class="view-source-button" for="get_exporter_format_rows-view-source"><span>View Source</span></label>

    </div>
    <a class="headerlink" href="#get_exporter_format_rows"></a>
            <div class="pdoc-code codehilite"><pre><span></span><span id="get_exporter_format_rows-430"><a href="#get_exporter_format_rows-430"><span class="linenos">430</span></a><span class="k">def</span><span class="w"> </span><span class="nf">get_exporter_format_rows</span><span class="p">(</span><span class="n">category</span><span class="o">=</span><span class="s2">&quot;exporter&quot;</span><span class="p">,</span> <span class="n">groups</span><span class="o">=</span><span class="p">(</span><span class="s2">&quot;system&quot;</span><span class="p">,</span> <span class="s2">&quot;extra&quot;</span><span class="p">,</span> <span class="s2">&quot;local&quot;</span><span class="p">)):</span>
</span><span id="get_exporter_format_rows-431"><a href="#get_exporter_format_rows-431"><span class="linenos">431</span></a><span class="w">    </span><span class="sd">&quot;&quot;&quot;</span>
</span><span id="get_exporter_format_rows-432"><a href="#get_exporter_format_rows-432"><span class="linenos">432</span></a><span class="sd">    Collect format_desc from all exporter plugins and return rows for the README table.</span>
</span><span id="get_exporter_format_rows-433"><a href="#get_exporter_format_rows-433"><span class="linenos">433</span></a>
</span><span id="get_exporter_format_rows-434"><a href="#get_exporter_format_rows-434"><span class="linenos">434</span></a><span class="sd">    Each exporter module may define a ``format_desc`` dict with keys:</span>
</span><span id="get_exporter_format_rows-435"><a href="#get_exporter_format_rows-435"><span class="linenos">435</span></a><span class="sd">      aliases: list of option names (e.g. [&quot;g&quot;, &quot;gromacs&quot;])</span>
</span><span id="get_exporter_format_rows-436"><a href="#get_exporter_format_rows-436"><span class="linenos">436</span></a><span class="sd">      application: str (markdown allowed)</span>
</span><span id="get_exporter_format_rows-437"><a href="#get_exporter_format_rows-437"><span class="linenos">437</span></a><span class="sd">      extension: str (e.g. &quot;.gro&quot;)</span>
</span><span id="get_exporter_format_rows-438"><a href="#get_exporter_format_rows-438"><span class="linenos">438</span></a><span class="sd">      water: str (e.g. &quot;Atomic positions&quot;)</span>
</span><span id="get_exporter_format_rows-439"><a href="#get_exporter_format_rows-439"><span class="linenos">439</span></a><span class="sd">      solute: str</span>
</span><span id="get_exporter_format_rows-440"><a href="#get_exporter_format_rows-440"><span class="linenos">440</span></a><span class="sd">      hb: str (e.g. &quot;none&quot;, &quot;o&quot;, &quot;auto&quot;)</span>
</span><span id="get_exporter_format_rows-441"><a href="#get_exporter_format_rows-441"><span class="linenos">441</span></a><span class="sd">      remarks: str</span>
</span><span id="get_exporter_format_rows-442"><a href="#get_exporter_format_rows-442"><span class="linenos">442</span></a><span class="sd">      suboptions: str (optional; short description of :key value options, e.g. &quot;water_model: 3site, 4site, 6site, tip4p&quot;)</span>
</span><span id="get_exporter_format_rows-443"><a href="#get_exporter_format_rows-443"><span class="linenos">443</span></a>
</span><span id="get_exporter_format_rows-444"><a href="#get_exporter_format_rows-444"><span class="linenos">444</span></a><span class="sd">    Returns a list of dicts with keys name, application, extension, water, solute, hb, remarks, suboptions.</span>
</span><span id="get_exporter_format_rows-445"><a href="#get_exporter_format_rows-445"><span class="linenos">445</span></a><span class="sd">    &quot;&quot;&quot;</span>
</span><span id="get_exporter_format_rows-446"><a href="#get_exporter_format_rows-446"><span class="linenos">446</span></a>    <span class="n">logger</span> <span class="o">=</span> <span class="n">getLogger</span><span class="p">()</span>
</span><span id="get_exporter_format_rows-447"><a href="#get_exporter_format_rows-447"><span class="linenos">447</span></a>    <span class="n">mods</span> <span class="o">=</span> <span class="n">scan</span><span class="p">(</span><span class="n">category</span><span class="p">)</span>
</span><span id="get_exporter_format_rows-448"><a href="#get_exporter_format_rows-448"><span class="linenos">448</span></a>    <span class="n">rows</span> <span class="o">=</span> <span class="p">[]</span>
</span><span id="get_exporter_format_rows-449"><a href="#get_exporter_format_rows-449"><span class="linenos">449</span></a>    <span class="n">seen</span> <span class="o">=</span> <span class="nb">set</span><span class="p">()</span>
</span><span id="get_exporter_format_rows-450"><a href="#get_exporter_format_rows-450"><span class="linenos">450</span></a>
</span><span id="get_exporter_format_rows-451"><a href="#get_exporter_format_rows-451"><span class="linenos">451</span></a>    <span class="k">for</span> <span class="n">group</span> <span class="ow">in</span> <span class="n">groups</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-452"><a href="#get_exporter_format_rows-452"><span class="linenos">452</span></a>        <span class="k">for</span> <span class="n">name</span> <span class="ow">in</span> <span class="n">mods</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="n">group</span><span class="p">,</span> <span class="p">[]):</span>
</span><span id="get_exporter_format_rows-453"><a href="#get_exporter_format_rows-453"><span class="linenos">453</span></a>            <span class="k">if</span> <span class="n">name</span> <span class="ow">in</span> <span class="n">seen</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-454"><a href="#get_exporter_format_rows-454"><span class="linenos">454</span></a>                <span class="k">continue</span>
</span><span id="get_exporter_format_rows-455"><a href="#get_exporter_format_rows-455"><span class="linenos">455</span></a>            <span class="k">try</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-456"><a href="#get_exporter_format_rows-456"><span class="linenos">456</span></a>                <span class="k">if</span> <span class="n">group</span> <span class="o">==</span> <span class="s2">&quot;system&quot;</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-457"><a href="#get_exporter_format_rows-457"><span class="linenos">457</span></a>                    <span class="n">mod</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;genice3.</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="get_exporter_format_rows-458"><a href="#get_exporter_format_rows-458"><span class="linenos">458</span></a>                <span class="k">elif</span> <span class="n">group</span> <span class="o">==</span> <span class="s2">&quot;extra&quot;</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-459"><a href="#get_exporter_format_rows-459"><span class="linenos">459</span></a>                    <span class="n">mod</span> <span class="o">=</span> <span class="kc">None</span>
</span><span id="get_exporter_format_rows-460"><a href="#get_exporter_format_rows-460"><span class="linenos">460</span></a>                    <span class="k">for</span> <span class="n">ep</span> <span class="ow">in</span> <span class="n">entry_points</span><span class="p">(</span><span class="n">group</span><span class="o">=</span><span class="sa">f</span><span class="s2">&quot;genice3_</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">):</span>
</span><span id="get_exporter_format_rows-461"><a href="#get_exporter_format_rows-461"><span class="linenos">461</span></a>                        <span class="k">if</span> <span class="n">ep</span><span class="o">.</span><span class="n">name</span> <span class="o">==</span> <span class="n">name</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-462"><a href="#get_exporter_format_rows-462"><span class="linenos">462</span></a>                            <span class="n">mod</span> <span class="o">=</span> <span class="n">ep</span><span class="o">.</span><span class="n">load</span><span class="p">()</span>
</span><span id="get_exporter_format_rows-463"><a href="#get_exporter_format_rows-463"><span class="linenos">463</span></a>                            <span class="k">break</span>
</span><span id="get_exporter_format_rows-464"><a href="#get_exporter_format_rows-464"><span class="linenos">464</span></a>                    <span class="k">if</span> <span class="n">mod</span> <span class="ow">is</span> <span class="kc">None</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-465"><a href="#get_exporter_format_rows-465"><span class="linenos">465</span></a>                        <span class="k">continue</span>
</span><span id="get_exporter_format_rows-466"><a href="#get_exporter_format_rows-466"><span class="linenos">466</span></a>                <span class="k">else</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-467"><a href="#get_exporter_format_rows-467"><span class="linenos">467</span></a>                    <span class="k">try</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-468"><a href="#get_exporter_format_rows-468"><span class="linenos">468</span></a>                        <span class="n">mod</span> <span class="o">=</span> <span class="n">importlib</span><span class="o">.</span><span class="n">import_module</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">category</span><span class="si">}</span><span class="s2">.</span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="get_exporter_format_rows-469"><a href="#get_exporter_format_rows-469"><span class="linenos">469</span></a>                    <span class="k">except</span> <span class="ne">ModuleNotFoundError</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-470"><a href="#get_exporter_format_rows-470"><span class="linenos">470</span></a>                        <span class="k">continue</span>
</span><span id="get_exporter_format_rows-471"><a href="#get_exporter_format_rows-471"><span class="linenos">471</span></a>                <span class="k">if</span> <span class="ow">not</span> <span class="nb">hasattr</span><span class="p">(</span><span class="n">mod</span><span class="p">,</span> <span class="s2">&quot;format_desc&quot;</span><span class="p">):</span>
</span><span id="get_exporter_format_rows-472"><a href="#get_exporter_format_rows-472"><span class="linenos">472</span></a>                    <span class="k">continue</span>
</span><span id="get_exporter_format_rows-473"><a href="#get_exporter_format_rows-473"><span class="linenos">473</span></a>                <span class="n">fd</span> <span class="o">=</span> <span class="n">mod</span><span class="o">.</span><span class="n">format_desc</span>
</span><span id="get_exporter_format_rows-474"><a href="#get_exporter_format_rows-474"><span class="linenos">474</span></a>                <span class="n">aliases</span> <span class="o">=</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;aliases&quot;</span><span class="p">,</span> <span class="p">[</span><span class="n">name</span><span class="p">])</span>
</span><span id="get_exporter_format_rows-475"><a href="#get_exporter_format_rows-475"><span class="linenos">475</span></a>                <span class="n">name_col</span> <span class="o">=</span> <span class="s2">&quot;, &quot;</span><span class="o">.</span><span class="n">join</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;`</span><span class="si">{</span><span class="n">a</span><span class="si">}</span><span class="s2">`&quot;</span> <span class="k">for</span> <span class="n">a</span> <span class="ow">in</span> <span class="n">aliases</span><span class="p">)</span>
</span><span id="get_exporter_format_rows-476"><a href="#get_exporter_format_rows-476"><span class="linenos">476</span></a>                <span class="n">rows</span><span class="o">.</span><span class="n">append</span><span class="p">(</span>
</span><span id="get_exporter_format_rows-477"><a href="#get_exporter_format_rows-477"><span class="linenos">477</span></a>                    <span class="p">{</span>
</span><span id="get_exporter_format_rows-478"><a href="#get_exporter_format_rows-478"><span class="linenos">478</span></a>                        <span class="s2">&quot;name&quot;</span><span class="p">:</span> <span class="n">name_col</span><span class="p">,</span>
</span><span id="get_exporter_format_rows-479"><a href="#get_exporter_format_rows-479"><span class="linenos">479</span></a>                        <span class="s2">&quot;application&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;application&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="get_exporter_format_rows-480"><a href="#get_exporter_format_rows-480"><span class="linenos">480</span></a>                        <span class="s2">&quot;extension&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;extension&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="get_exporter_format_rows-481"><a href="#get_exporter_format_rows-481"><span class="linenos">481</span></a>                        <span class="s2">&quot;water&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;water&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="get_exporter_format_rows-482"><a href="#get_exporter_format_rows-482"><span class="linenos">482</span></a>                        <span class="s2">&quot;solute&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;solute&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="get_exporter_format_rows-483"><a href="#get_exporter_format_rows-483"><span class="linenos">483</span></a>                        <span class="s2">&quot;hb&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;hb&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="get_exporter_format_rows-484"><a href="#get_exporter_format_rows-484"><span class="linenos">484</span></a>                        <span class="s2">&quot;remarks&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;remarks&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="get_exporter_format_rows-485"><a href="#get_exporter_format_rows-485"><span class="linenos">485</span></a>                        <span class="s2">&quot;suboptions&quot;</span><span class="p">:</span> <span class="n">fd</span><span class="o">.</span><span class="n">get</span><span class="p">(</span><span class="s2">&quot;suboptions&quot;</span><span class="p">,</span> <span class="s2">&quot;&quot;</span><span class="p">),</span>
</span><span id="get_exporter_format_rows-486"><a href="#get_exporter_format_rows-486"><span class="linenos">486</span></a>                    <span class="p">}</span>
</span><span id="get_exporter_format_rows-487"><a href="#get_exporter_format_rows-487"><span class="linenos">487</span></a>                <span class="p">)</span>
</span><span id="get_exporter_format_rows-488"><a href="#get_exporter_format_rows-488"><span class="linenos">488</span></a>                <span class="n">seen</span><span class="o">.</span><span class="n">add</span><span class="p">(</span><span class="n">name</span><span class="p">)</span>
</span><span id="get_exporter_format_rows-489"><a href="#get_exporter_format_rows-489"><span class="linenos">489</span></a>            <span class="k">except</span> <span class="ne">Exception</span> <span class="k">as</span> <span class="n">e</span><span class="p">:</span>
</span><span id="get_exporter_format_rows-490"><a href="#get_exporter_format_rows-490"><span class="linenos">490</span></a>                <span class="n">logger</span><span class="o">.</span><span class="n">debug</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;Skip </span><span class="si">{</span><span class="n">name</span><span class="si">}</span><span class="s2"> for format table: </span><span class="si">{</span><span class="n">e</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
</span><span id="get_exporter_format_rows-491"><a href="#get_exporter_format_rows-491"><span class="linenos">491</span></a>    <span class="k">return</span> <span class="n">rows</span>
</span></pre></div>


            <div class="docstring"><p>Collect format_desc from all exporter plugins and return rows for the README table.</p>

<p>Each exporter module may define a <code>format_desc</code> dict with keys:
  aliases: list of option names (e.g. ["g", "gromacs"])
  application: str (markdown allowed)
  extension: str (e.g. ".gro")
  water: str (e.g. "Atomic positions")
  solute: str
  hb: str (e.g. "none", "o", "auto")
  remarks: str
  suboptions: str (optional; short description of :key value options, e.g. "water_model: 3site, 4site, 6site, tip4p")</p>

<p>Returns a list of dicts with keys name, application, extension, water, solute, hb, remarks, suboptions.</p>
</div>


                </section>
    </main>
<script>
    function escapeHTML(html) {
        return document.createElement('div').appendChild(document.createTextNode(html)).parentNode.innerHTML;
    }

    const originalContent = document.querySelector("main.pdoc");
    let currentContent = originalContent;

    function setContent(innerHTML) {
        let elem;
        if (innerHTML) {
            elem = document.createElement("main");
            elem.classList.add("pdoc");
            elem.innerHTML = innerHTML;
        } else {
            elem = originalContent;
        }
        if (currentContent !== elem) {
            currentContent.replaceWith(elem);
            currentContent = elem;
        }
    }

    function getSearchTerm() {
        return (new URL(window.location)).searchParams.get("search");
    }

    const searchBox = document.querySelector(".pdoc input[type=search]");
    searchBox.addEventListener("input", function () {
        let url = new URL(window.location);
        if (searchBox.value.trim()) {
            url.hash = "";
            url.searchParams.set("search", searchBox.value);
        } else {
            url.searchParams.delete("search");
        }
        history.replaceState("", "", url.toString());
        onInput();
    });
    window.addEventListener("popstate", onInput);


    let search, searchErr;

    async function initialize() {
        try {
            search = await new Promise((resolve, reject) => {
                const script = document.createElement("script");
                script.type = "text/javascript";
                script.async = true;
                script.onload = () => resolve(window.pdocSearch);
                script.onerror = (e) => reject(e);
                script.src = "../search.js";
                document.getElementsByTagName("head")[0].appendChild(script);
            });
        } catch (e) {
            console.error("Cannot fetch pdoc search index");
            searchErr = "Cannot fetch search index.";
        }
        onInput();

        document.querySelector("nav.pdoc").addEventListener("click", e => {
            if (e.target.hash) {
                searchBox.value = "";
                searchBox.dispatchEvent(new Event("input"));
            }
        });
    }

    function onInput() {
        setContent((() => {
            const term = getSearchTerm();
            if (!term) {
                return null
            }
            if (searchErr) {
                return `<h3>Error: ${searchErr}</h3>`
            }
            if (!search) {
                return "<h3>Searching...</h3>"
            }

            window.scrollTo({top: 0, left: 0, behavior: 'auto'});

            const results = search(term);

            let html;
            if (results.length === 0) {
                html = `No search results for '${escapeHTML(term)}'.`
            } else {
                html = `<h4>${results.length} search result${results.length > 1 ? "s" : ""} for '${escapeHTML(term)}'.</h4>`;
            }
            for (let result of results.slice(0, 10)) {
                let doc = result.doc;
                let url = `../${doc.modulename.replaceAll(".", "/")}.html`;
                if (doc.qualname) {
                    url += `#${doc.qualname}`;
                }

                let heading;
                switch (result.doc.kind) {
                    case "function":
                        if (doc.fullname.endsWith(".__init__")) {
                            heading = `<span class="name">${doc.fullname.replace(/\.__init__$/, "")}</span>${doc.signature}`;
                        } else {
                            heading = `<span class="def">${doc.funcdef}</span> <span class="name">${doc.fullname}</span>${doc.signature}`;
                        }
                        break;
                    case "class":
                        heading = `<span class="def">class</span> <span class="name">${doc.fullname}</span>`;
                        if (doc.bases)
                            heading += `<wbr>(<span class="base">${doc.bases}</span>)`;
                        heading += `:`;
                        break;
                    case "variable":
                        heading = `<span class="name">${doc.fullname}</span>`;
                        if (doc.annotation)
                            heading += `<span class="annotation">${doc.annotation}</span>`;
                        if (doc.default_value)
                            heading += `<span class="default_value"> = ${doc.default_value}</span>`;
                        break;
                    default:
                        heading = `<span class="name">${doc.fullname}</span>`;
                        break;
                }
                html += `
                        <section class="search-result">
                        <a href="${url}" class="attr ${doc.kind}">${heading}</a>
                        <div class="docstring">${doc.doc}</div>
                        </section>
                    `;

            }
            return html;
        })());
    }

    if (getSearchTerm()) {
        initialize();
        searchBox.value = getSearchTerm();
        onInput();
    } else {
        searchBox.addEventListener("focus", initialize, {once: true});
    }

    searchBox.addEventListener("keydown", e => {
        if (["ArrowDown", "ArrowUp", "Enter"].includes(e.key)) {
            let focused = currentContent.querySelector(".search-result.focused");
            if (!focused) {
                currentContent.querySelector(".search-result").classList.add("focused");
            } else if (
                e.key === "ArrowDown"
                && focused.nextElementSibling
                && focused.nextElementSibling.classList.contains("search-result")
            ) {
                focused.classList.remove("focused");
                focused.nextElementSibling.classList.add("focused");
                focused.nextElementSibling.scrollIntoView({
                    behavior: "smooth",
                    block: "nearest",
                    inline: "nearest"
                });
            } else if (
                e.key === "ArrowUp"
                && focused.previousElementSibling
                && focused.previousElementSibling.classList.contains("search-result")
            ) {
                focused.classList.remove("focused");
                focused.previousElementSibling.classList.add("focused");
                focused.previousElementSibling.scrollIntoView({
                    behavior: "smooth",
                    block: "nearest",
                    inline: "nearest"
                });
            } else if (
                e.key === "Enter"
            ) {
                focused.querySelector("a").click();
            }
        }
    });
</script>
pre{line-height:125%;}span.linenos{color:inherit; background-color:transparent; padding-left:5px; padding-right:20px;}.pdoc-code .hll{background-color:#ffffcc}.pdoc-code{background:#f8f8f8;}.pdoc-code .c{color:#3D7B7B; font-style:italic}.pdoc-code .err{border:1px solid #FF0000}.pdoc-code .k{color:#008000; font-weight:bold}.pdoc-code .o{color:#666666}.pdoc-code .ch{color:#3D7B7B; font-style:italic}.pdoc-code .cm{color:#3D7B7B; font-style:italic}.pdoc-code .cp{color:#9C6500}.pdoc-code .cpf{color:#3D7B7B; font-style:italic}.pdoc-code .c1{color:#3D7B7B; font-style:italic}.pdoc-code .cs{color:#3D7B7B; font-style:italic}.pdoc-code .gd{color:#A00000}.pdoc-code .ge{font-style:italic}.pdoc-code .gr{color:#E40000}.pdoc-code .gh{color:#000080; font-weight:bold}.pdoc-code .gi{color:#008400}.pdoc-code .go{color:#717171}.pdoc-code .gp{color:#000080; font-weight:bold}.pdoc-code .gs{font-weight:bold}.pdoc-code .gu{color:#800080; font-weight:bold}.pdoc-code .gt{color:#0044DD}.pdoc-code .kc{color:#008000; font-weight:bold}.pdoc-code .kd{color:#008000; font-weight:bold}.pdoc-code .kn{color:#008000; font-weight:bold}.pdoc-code .kp{color:#008000}.pdoc-code .kr{color:#008000; font-weight:bold}.pdoc-code .kt{color:#B00040}.pdoc-code .m{color:#666666}.pdoc-code .s{color:#BA2121}.pdoc-code .na{color:#687822}.pdoc-code .nb{color:#008000}.pdoc-code .nc{color:#0000FF; font-weight:bold}.pdoc-code .no{color:#880000}.pdoc-code .nd{color:#AA22FF}.pdoc-code .ni{color:#717171; font-weight:bold}.pdoc-code .ne{color:#CB3F38; font-weight:bold}.pdoc-code .nf{color:#0000FF}.pdoc-code .nl{color:#767600}.pdoc-code .nn{color:#0000FF; font-weight:bold}.pdoc-code .nt{color:#008000; font-weight:bold}.pdoc-code .nv{color:#19177C}.pdoc-code .ow{color:#AA22FF; font-weight:bold}.pdoc-code .w{color:#bbbbbb}.pdoc-code .mb{color:#666666}.pdoc-code .mf{color:#666666}.pdoc-code .mh{color:#666666}.pdoc-code .mi{color:#666666}.pdoc-code .mo{color:#666666}.pdoc-code .sa{color:#BA2121}.pdoc-code .sb{color:#BA2121}.pdoc-code .sc{color:#BA2121}.pdoc-code .dl{color:#BA2121}.pdoc-code .sd{color:#BA2121; font-style:italic}.pdoc-code .s2{color:#BA2121}.pdoc-code .se{color:#AA5D1F; font-weight:bold}.pdoc-code .sh{color:#BA2121}.pdoc-code .si{color:#A45A77; font-weight:bold}.pdoc-code .sx{color:#008000}.pdoc-code .sr{color:#A45A77}.pdoc-code .s1{color:#BA2121}.pdoc-code .ss{color:#19177C}.pdoc-code .bp{color:#008000}.pdoc-code .fm{color:#0000FF}.pdoc-code .vc{color:#19177C}.pdoc-code .vg{color:#19177C}.pdoc-code .vi{color:#19177C}.pdoc-code .vm{color:#19177C}.pdoc-code .il{color:#666666}:root{--pdoc-background:#fff;}.pdoc{--text:#212529;--muted:#6c757d;--link:#3660a5;--link-hover:#1659c5;--code:#f8f8f8;--active:#fff598;--accent:#eee;--accent2:#c1c1c1;--nav-hover:rgba(255, 255, 255, 0.5);--name:#0066BB;--def:#008800;--annotation:#007020;}.pdoc{color:var(--text);box-sizing:border-box;line-height:1.5;background:none;}.pdoc .pdoc-button{cursor:pointer;display:inline-block;border:solid black 1px;border-radius:2px;font-size:.75rem;padding:calc(0.5em - 1px) 1em;transition:100ms all;}.pdoc .alert{padding:1rem 1rem 1rem calc(1.5rem + 24px);border:1px solid transparent;border-radius:.25rem;background-repeat:no-repeat;background-position:.75rem center;margin-bottom:1rem;}.pdoc .alert > em{display:none;}.pdoc .alert > *:last-child{margin-bottom:0;}.pdoc .alert.note{color:#084298;background-color:#cfe2ff;border-color:#b6d4fe;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2224%22%20height%3D%2224%22%20fill%3D%22%23084298%22%20viewBox%3D%220%200%2016%2016%22%3E%3Cpath%20d%3D%22M8%2016A8%208%200%201%200%208%200a8%208%200%200%200%200%2016zm.93-9.412-1%204.705c-.07.34.029.533.304.533.194%200%20.487-.07.686-.246l-.088.416c-.287.346-.92.598-1.465.598-.703%200-1.002-.422-.808-1.319l.738-3.468c.064-.293.006-.399-.287-.47l-.451-.081.082-.381%202.29-.287zM8%205.5a1%201%200%201%201%200-2%201%201%200%200%201%200%202z%22/%3E%3C/svg%3E");}.pdoc .alert.tip{color:#0a3622;background-color:#d1e7dd;border-color:#a3cfbb;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2224%22%20height%3D%2224%22%20fill%3D%22%230a3622%22%20viewBox%3D%220%200%2016%2016%22%3E%3Cpath%20d%3D%22M2%206a6%206%200%201%201%2010.174%204.31c-.203.196-.359.4-.453.619l-.762%201.769A.5.5%200%200%201%2010.5%2013a.5.5%200%200%201%200%201%20.5.5%200%200%201%200%201l-.224.447a1%201%200%200%201-.894.553H6.618a1%201%200%200%201-.894-.553L5.5%2015a.5.5%200%200%201%200-1%20.5.5%200%200%201%200-1%20.5.5%200%200%201-.46-.302l-.761-1.77a2%202%200%200%200-.453-.618A5.98%205.98%200%200%201%202%206m6-5a5%205%200%200%200-3.479%208.592c.263.254.514.564.676.941L5.83%2012h4.342l.632-1.467c.162-.377.413-.687.676-.941A5%205%200%200%200%208%201%22/%3E%3C/svg%3E");}.pdoc .alert.important{color:#055160;background-color:#cff4fc;border-color:#9eeaf9;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2224%22%20height%3D%2224%22%20fill%3D%22%23055160%22%20viewBox%3D%220%200%2016%2016%22%3E%3Cpath%20d%3D%22M2%200a2%202%200%200%200-2%202v12a2%202%200%200%200%202%202h12a2%202%200%200%200%202-2V2a2%202%200%200%200-2-2zm6%204c.535%200%20.954.462.9.995l-.35%203.507a.552.552%200%200%201-1.1%200L7.1%204.995A.905.905%200%200%201%208%204m.002%206a1%201%200%201%201%200%202%201%201%200%200%201%200-2%22/%3E%3C/svg%3E");}.pdoc .alert.warning{color:#664d03;background-color:#fff3cd;border-color:#ffecb5;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2224%22%20height%3D%2224%22%20fill%3D%22%23664d03%22%20viewBox%3D%220%200%2016%2016%22%3E%3Cpath%20d%3D%22M8.982%201.566a1.13%201.13%200%200%200-1.96%200L.165%2013.233c-.457.778.091%201.767.98%201.767h13.713c.889%200%201.438-.99.98-1.767L8.982%201.566zM8%205c.535%200%20.954.462.9.995l-.35%203.507a.552.552%200%200%201-1.1%200L7.1%205.995A.905.905%200%200%201%208%205zm.002%206a1%201%200%201%201%200%202%201%201%200%200%201%200-2z%22/%3E%3C/svg%3E");}.pdoc .alert.caution{color:#842029;background-color:#f8d7da;border-color:#f5c2c7;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2224%22%20height%3D%2224%22%20fill%3D%22%23842029%22%20viewBox%3D%220%200%2016%2016%22%3E%3Cpath%20d%3D%22M11.46.146A.5.5%200%200%200%2011.107%200H4.893a.5.5%200%200%200-.353.146L.146%204.54A.5.5%200%200%200%200%204.893v6.214a.5.5%200%200%200%20.146.353l4.394%204.394a.5.5%200%200%200%20.353.146h6.214a.5.5%200%200%200%20.353-.146l4.394-4.394a.5.5%200%200%200%20.146-.353V4.893a.5.5%200%200%200-.146-.353zM8%204c.535%200%20.954.462.9.995l-.35%203.507a.552.552%200%200%201-1.1%200L7.1%204.995A.905.905%200%200%201%208%204m.002%206a1%201%200%201%201%200%202%201%201%200%200%201%200-2%22/%3E%3C/svg%3E");}.pdoc .alert.danger{color:#842029;background-color:#f8d7da;border-color:#f5c2c7;background-image:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2224%22%20height%3D%2224%22%20fill%3D%22%23842029%22%20viewBox%3D%220%200%2016%2016%22%3E%3Cpath%20d%3D%22M5.52.359A.5.5%200%200%201%206%200h4a.5.5%200%200%201%20.474.658L8.694%206H12.5a.5.5%200%200%201%20.395.807l-7%209a.5.5%200%200%201-.873-.454L6.823%209.5H3.5a.5.5%200%200%201-.48-.641l2.5-8.5z%22/%3E%3C/svg%3E");}.pdoc .visually-hidden{position:absolute !important;width:1px !important;height:1px !important;padding:0 !important;margin:-1px !important;overflow:hidden !important;clip:rect(0, 0, 0, 0) !important;white-space:nowrap !important;border:0 !important;}.pdoc h1, .pdoc h2, .pdoc h3{font-weight:300;margin:.3em 0;padding:.2em 0;}.pdoc > section:not(.module-info) h1{font-size:1.5rem;font-weight:500;}.pdoc > section:not(.module-info) h2{font-size:1.4rem;font-weight:500;}.pdoc > section:not(.module-info) h3{font-size:1.3rem;font-weight:500;}.pdoc > section:not(.module-info) h4{font-size:1.2rem;}.pdoc > section:not(.module-info) h5{font-size:1.1rem;}.pdoc a{text-decoration:none;color:var(--link);}.pdoc a:hover{color:var(--link-hover);}.pdoc blockquote{margin-left:2rem;}.pdoc pre{border-top:1px solid var(--accent2);border-bottom:1px solid var(--accent2);margin-top:0;margin-bottom:1em;padding:.5rem 0 .5rem .5rem;overflow-x:auto;background-color:var(--code);}.pdoc code{color:var(--text);padding:.2em .4em;margin:0;font-size:85%;background-color:var(--accent);border-radius:6px;}.pdoc a > code{color:inherit;}.pdoc pre > code{display:inline-block;font-size:inherit;background:none;border:none;padding:0;}.pdoc > section:not(.module-info){margin-bottom:1.5rem;}.pdoc .modulename{margin-top:0;font-weight:bold;}.pdoc .modulename a{color:var(--link);transition:100ms all;}.pdoc .git-button{float:right;border:solid var(--link) 1px;}.pdoc .git-button:hover{background-color:var(--link);color:var(--pdoc-background);}.view-source-toggle-state,.view-source-toggle-state ~ .pdoc-code{display:none;}.view-source-toggle-state:checked ~ .pdoc-code{display:block;}.view-source-button{display:inline-block;float:right;font-size:.75rem;line-height:1.5rem;color:var(--muted);padding:0 .4rem 0 1.3rem;cursor:pointer;text-indent:-2px;}.view-source-button > span{visibility:hidden;}.module-info .view-source-button{float:none;display:flex;justify-content:flex-end;margin:-1.2rem .4rem -.2rem 0;}.view-source-button::before{position:absolute;content:"View Source";display:list-item;list-style-type:disclosure-closed;}.view-source-toggle-state:checked ~ .attr .view-source-button::before,.view-source-toggle-state:checked ~ .view-source-button::before{list-style-type:disclosure-open;}.pdoc .docstring{margin-bottom:1.5rem;}.pdoc section:not(.module-info) .docstring{margin-left:clamp(0rem, 5vw - 2rem, 1rem);}.pdoc .docstring .pdoc-code{margin-left:1em;margin-right:1em;}.pdoc h1:target,.pdoc h2:target,.pdoc h3:target,.pdoc h4:target,.pdoc h5:target,.pdoc h6:target,.pdoc .pdoc-code > pre > span:target{background-color:var(--active);box-shadow:-1rem 0 0 0 var(--active);}.pdoc .pdoc-code > pre > span:target{display:block;}.pdoc div:target > .attr,.pdoc section:target > .attr,.pdoc dd:target > a{background-color:var(--active);}.pdoc *{scroll-margin:2rem;}.pdoc .pdoc-code .linenos{user-select:none;}.pdoc .attr:hover{filter:contrast(0.95);}.pdoc section, .pdoc .classattr{position:relative;}.pdoc .headerlink{--width:clamp(1rem, 3vw, 2rem);position:absolute;top:0;left:calc(0rem - var(--width));transition:all 100ms ease-in-out;opacity:0;}.pdoc .headerlink::before{content:"#";display:block;text-align:center;width:var(--width);height:2.3rem;line-height:2.3rem;font-size:1.5rem;}.pdoc .attr:hover ~ .headerlink,.pdoc *:target > .headerlink,.pdoc .headerlink:hover{opacity:1;}.pdoc .attr{display:block;margin:.5rem 0 .5rem;padding:.4rem .4rem .4rem 1rem;background-color:var(--accent);overflow-x:auto;}.pdoc .classattr{margin-left:2rem;}.pdoc .decorator-deprecated{color:#842029;}.pdoc .decorator-deprecated ~ span{filter:grayscale(1) opacity(0.8);}.pdoc .name{color:var(--name);font-weight:bold;}.pdoc .def{color:var(--def);font-weight:bold;}.pdoc .signature{background-color:transparent;}.pdoc .param, .pdoc .return-annotation{white-space:pre;}.pdoc .signature.multiline .param{display:block;}.pdoc .signature.condensed .param{display:inline-block;}.pdoc .annotation{color:var(--annotation);}.pdoc .view-value-toggle-state,.pdoc .view-value-toggle-state ~ .default_value{display:none;}.pdoc .view-value-toggle-state:checked ~ .default_value{display:inherit;}.pdoc .view-value-button{font-size:.5rem;vertical-align:middle;border-style:dashed;margin-top:-0.1rem;}.pdoc .view-value-button:hover{background:white;}.pdoc .view-value-button::before{content:"show";text-align:center;width:2.2em;display:inline-block;}.pdoc .view-value-toggle-state:checked ~ .view-value-button::before{content:"hide";}.pdoc .inherited{margin-left:2rem;}.pdoc .inherited dt{font-weight:700;}.pdoc .inherited dt, .pdoc .inherited dd{display:inline;margin-left:0;margin-bottom:.5rem;}.pdoc .inherited dd:not(:last-child):after{content:", ";}.pdoc .inherited .class:before{content:"class ";}.pdoc .inherited .function a:after{content:"()";}.pdoc .search-result .docstring{overflow:auto;max-height:25vh;}.pdoc .search-result.focused > .attr{background-color:var(--active);}.pdoc .attribution{margin-top:2rem;display:block;opacity:0.5;transition:all 200ms;filter:grayscale(100%);}.pdoc .attribution:hover{opacity:1;filter:grayscale(0%);}.pdoc .attribution img{margin-left:5px;height:27px;vertical-align:bottom;width:50px;transition:all 200ms;}.pdoc table{display:block;width:max-content;max-width:100%;overflow:auto;margin-bottom:1rem;}.pdoc table th{font-weight:600;}.pdoc table th, .pdoc table td{padding:6px 13px;border:1px solid var(--accent2);}