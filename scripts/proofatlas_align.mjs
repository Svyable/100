// Offline alignment candidates; no equivalence, status, or registry writes.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
function align(atlas, registry) {
  const require=(ok,msg)=>{if(!ok)throw Error(msg)};
  require(atlas.publicationId==="proofatlas.open-problem-ranking.top500.v35"&&atlas.editionDate==="2026-11-12"&&atlas.recordCount===500,"wrong atlas edition");
  require(Array.isArray(atlas.records)&&atlas.records.length===500,"expected 500 records");
  require(Array.isArray(registry)&&registry.length===100,"expected 100 active records");
  const ranks=new Set(), atlasIds=new Set(), projectIds=new Set();
  const normalize=s=>s.normalize("NFKD").replace(/\p{M}/gu,"").toLowerCase().replace(/[^a-z0-9]+/g," ").trim();
  for(const row of atlas.records){
    require(typeof row.problemId==="string"&&row.problemId.length>0&&!atlasIds.has(row.problemId),"duplicate/missing atlas ID");
    require(Number.isInteger(row.releaseRank)&&row.releaseRank>=1&&row.releaseRank<=500&&!ranks.has(row.releaseRank),"invalid/duplicate rank");
    require(typeof row.canonicalTitle==="string"&&row.canonicalTitle.trim()&&typeof row.exactTarget==="string"&&row.exactTarget.trim(),"missing title or target");
    ranks.add(row.releaseRank);atlasIds.add(row.problemId);
  }
  const titles=new Map();
  for(const p of registry){
    require(/^M(?:0[0-9]{2}|100)$/.test(p.id)&&p.id!=="M000"&&!projectIds.has(p.id)&&typeof p.name==="string"&&p.name.trim()&&typeof p.question==="string"&&p.question.trim(),"invalid active record");
    projectIds.add(p.id);
    const key=normalize(p.name);
    if(!titles.has(key))titles.set(key,[]);
    titles.get(key).push(p.id);
  }
  const mappings=[[1,"M081","P versus NP"],[2,"M001","Riemann Hypothesis"],[3,"M091","Yang-Mills Existence and Mass Gap"],[4,"M021","Hodge Conjecture"],[6,"M003","Birch and Swinnerton-Dyer Conjecture"],[7,"M017","Global Langlands Functoriality Conjecture"],[9,"M004","The abc Conjecture of Masser and Oesterle"],[10,"M002","Generalized Riemann Hypothesis for Dirichlet L-functions"],[11,"M082","NP versus coNP Problem"],[23,"M022","Grothendiecks Generalized Hodge Conjecture"],[24,"M006","Binary Goldbach Problem for Even Integers"],[26,"M011","Schanuel's conjecture"],[27,"M084","Matrix-Multiplication Exponent Equals Two"],[31,"M083","Valiants Algebraic P versus NP Conjecture (VP != VNP)"],[169,"M097","Metric TSP Subtour LP Integrality Gap Conjecture"]];
  const seeds=new Map(mappings.map(([rank,id,title])=>[rank,{id,title}]));
  const proposals=new Set([5,8,170]);
  const rows=atlas.records.slice().sort((a,b)=>a.releaseRank-b.releaseRank).map(r=>{
    const seed=seeds.get(r.releaseRank);
    const matches=new Set(titles.get(normalize(r.canonicalTitle))||[]);
    if(seed&&projectIds.has(seed.id)&&normalize(seed.title)===normalize(r.canonicalTitle))matches.add(seed.id);
    return {rank:r.releaseRank,atlas_id:r.problemId,title:r.canonicalTitle,candidates:[...matches].sort(),manual_admission_lead:proposals.has(r.releaseRank),relation:"unreviewed_candidate_only",external_status:r.releaseStatus??null};
  });
  return {publication_id:atlas.publicationId,rows,summary:{records:rows.length,rows_with_candidates:rows.filter(r=>r.candidates.length).length,exact_equivalence_certified:0,unmatched_is_not_absent:true},registry_changed:false};
}
function selfTest(){
  const registry=Array.from({length:100},(_,i)=>({id:"M"+String(i+1).padStart(3,"0"),name:"local "+i,question:"synthetic target "+i}));
  registry[80].name="P versus NP";
  const atlas={publicationId:"proofatlas.open-problem-ranking.top500.v35",editionDate:"2026-11-12",recordCount:500,records:Array.from({length:500},(_,i)=>({problemId:"synthetic."+i,releaseRank:i+1,canonicalTitle:i===0?"P versus NP":"external "+i,exactTarget:"synthetic target "+i,releaseStatus:"open"}))};
  const snapshot=JSON.stringify(registry),res=align(atlas,registry);
  if(res.rows.length!==500||res.rows[0].candidates[0]!=="M081"||res.summary.exact_equivalence_certified!==0||JSON.stringify(registry)!==snapshot)throw Error("alignment test failed");
  const mutants=[x=>x.publicationId="wrong",x=>x.records.pop(),x=>x.records[1].releaseRank=1,x=>x.records[1].problemId=x.records[0].problemId,x=>x.records[0].exactTarget=""];
  let rejected=0;
  for(const mutate of mutants){const x=JSON.parse(JSON.stringify(atlas));mutate(x);try{align(x,registry)}catch{rejected++;continue}throw Error("mutant survived")}
  return {fixture_records:500,mutants_rejected:rejected,real_atlas_records_processed:0,registry_unchanged:true};
}
if(process.argv[2]==="--self-test") console.log(JSON.stringify(selfTest(),null,2));
else {
 if(process.argv.length!==4) throw Error("usage: node scripts/proofatlas_align.mjs atlas.json data/problems.json");
 const atlas=readFileSync(process.argv[2]),registry=readFileSync(process.argv[3]);
 const result=align(JSON.parse(atlas),JSON.parse(registry));
 const digest=x=>createHash("sha256").update(x).digest("hex");
 console.log(JSON.stringify({...result,atlas_sha256:digest(atlas),registry_sha256:digest(registry)},null,2));
}
