// X-COGENTIC-2026-INTAKE: finite source/scope controls, not proof replay.
import { readFileSync } from "node:fs";
function validate(m) {
  const expected = ["integer_factorization","discrete_logarithm","bimatrix_nash_equilibrium","deterministic_factoring_l34","logrank_conjecture","edge_reconstruction","fictitious_play_convergence","subadditive_prophet_inequalities","vc_sample_compression","ce_convex_games"];
  const check = (ok, why) => { if (!ok) throw Error(why); };
  check(m.version === 1 && m.source_repo === "google-research/google-research" && m.revision === "4a7bc8ab0bc770e71a259b7966c500496b99010a", "wrong source revision");
  check(m.papers.length === expected.length && new Set(m.papers.map(p=>p.id)).size === expected.length && expected.every(id=>m.papers.some(p=>p.id===id)), "missing or duplicate paper");
  for (const p of m.papers) {
    check(p.source_url === `https://github.com/${m.source_repo}/tree/${m.revision}/cogentic_research_papers/${p.id}`, "unpinned paper");
    check(/^[0-9a-f]{40}$/.test(p.readme_blob) && /^[0-9a-f]{40}$/.test(p.pdf_blob), "invalid Git blob identity");
    check(p.evidence === "author_claim_readme_only" && p.claim && p.scope_limit && p.next_task, "unsupported evidence or missing scope");
    check(Array.isArray(p.related) && p.related.every(id=>/^M(0[0-9]{2}|100)$/.test(id)), "invalid active mapping");
    check(p.lean_source_status === (p.lean_version_claimed ? "promised_not_in_directory" : "not_asserted_in_readme"), "unsupported Lean status");
    check((p.date === "2026-11-25") === Boolean(p.lean_version_claimed), "wrong companion release inventory");
    check(p.relation === (p.id === "edge_reconstruction" ? "related_not_equivalent" : "reservoir_candidate"), "scope promotion");
  }
  check(m.papers.find(p=>p.id==="edge_reconstruction").related.includes("M078"), "missing M078 scope link");
  check(new Set(m.papers.map(p=>p.pdf_blob)).size === expected.length, "duplicate PDF");
  return expected.length;
}
function edgeControl() {
  const check = (ok, why) => { if (!ok) throw Error(why); };
  function permutations(a) { return a.length===0?[[]]:a.flatMap((v,i)=>permutations(a.filter((_,j)=>i!==j)).map(p=>[v,...p])); }
  function canonical(vertices, edges) {
    return permutations(vertices).map(p=> {
      const mapped = new Set(edges.map(([u,v])=>[Math.min(p.indexOf(u),p.indexOf(v)),Math.max(p.indexOf(u),p.indexOf(v))].join(",")));
      let s="";
      for(let i=0;i<p.length;i++) for(let j=i+1;j<p.length;j++) s+=mapped.has(`${i},${j}`)?"1":"0";
      return s;
    }).sort()[0];
  }
  const v=[0,1,2,3], triangle=[[0,1],[1,2],[0,2]], star=[[0,1],[0,2],[0,3]];
  const edgeDeck=(es)=>es.map((_,i)=>canonical(v,es.filter((_,j)=>i!==j))).sort().join("|");
  const vertexDeck=(es)=>v.map(u=>canonical(v.filter(x=>x!==u),es.filter(e=>!e.includes(u)))).sort().join("|");
  check(canonical(v,triangle)!==canonical(v,star),"control graphs must be nonisomorphic");
  check(edgeDeck(triangle)===edgeDeck(star),"known three-edge collision lost");
  check(vertexDeck(triangle)!==vertexDeck(star),"vertex/edge deck distinction lost");
  let feasible=[];
  for(let n=4;n<=2001;n++) if(n*(n-1)/2>=1000*n) feasible.push(n);
  check(feasible.length===1&&feasible[0]===2001,"first feasible density threshold");
  return {first_feasible_n:2001,edge_collision:true,vertex_collision:false,in_scope:false};
}
function controls(m) {
  const mutations = [
    x=>x.papers.pop(),
    x=>x.papers[1]=x.papers[0],
    x=>x.papers[0].source_url=x.papers[0].source_url.replace(x.revision,"main"),
    x=>x.papers[0].pdf_blob="not-a-sha",
    x=>x.papers[0].evidence="accepted_independent",
    x=>x.papers[0].lean_source_status="replayed",
    x=>x.papers.find(p=>p.id==="edge_reconstruction").relation="equivalent",
    x=>x.papers.find(p=>p.id==="edge_reconstruction").related=[]
  ];
  let rejected=0;
  for(const mutate of mutations) {
    const x=JSON.parse(JSON.stringify(m)); mutate(x);
    try {validate(x);} catch(e) {rejected++;continue;}
    throw Error("mutation survived");
  }
  return {papers:validate(m),mutants_rejected:rejected,edge_control:edgeControl()};
}
const path=process.argv[2] || new URL("../data/cogentic_2026_intake.json", import.meta.url);
console.log(JSON.stringify(controls(JSON.parse(readFileSync(path,"utf8"))),null,2));
