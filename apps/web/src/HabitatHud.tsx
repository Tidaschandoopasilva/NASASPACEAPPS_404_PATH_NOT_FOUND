import { useState } from 'react';
import { equipmentLabels } from './conditions';
const resources: Record<string, string> = {
    oxygen_l: 'Oxygen · L', water_l: 'Water · L', suit_wh: 'Suit power · Wh',
    kit_wh: 'Science kit · Wh', robot_wh: 'Robot power · Wh', crew_minutes: 'Crew time · min', habitat_wh: 'Habitat power · Wh',
};

export default function HabitatHud({ state, run, progress, busy, reading, baseRunning, saveFailed, briefing, briefingBusy, onBriefing, onLaunch, onResume, onAdvance, onDiscard, onRecord, onPreview, onReplay }: any) {
    const [question,setQuestion] = useState('');
    if (!state) return null;
    const plan = run?.habitat;
    const elapsed = reading?.sol_elapsed ?? state.sol_elapsed;
    const clock = Math.floor(elapsed % 1 * 1440);
    const localClock = String(Math.floor(clock/60)).padStart(2,'0') + ':' + String(clock%60).padStart(2,'0');
    return <section className="mission-detail habitat-hud">
        <h3>Habitat campaign</h3>
        <p><strong>{state.completed} / {state.goal} EVA expeditions</strong> · {state.expeditions} recorded attempts</p>
        <p><strong>Sol {1+Math.floor(elapsed)} · {localClock}</strong> · {baseRunning ? 'Habitat cycle running' : reading?.active_sortie ? 'EVA ' + reading.active_sortie : 'Crew at habitat'}</p>
        {state.active_draft ? <div className="export-row">
            {state.active_draft !== plan?.id && <button disabled={busy} onClick={onResume}>Resume unrecorded expedition</button>}
            <button disabled={busy} onClick={onDiscard}>Discard unrecorded plan</button></div> :
            <div className="export-row"><button disabled={busy} onClick={() => onAdvance(1)}>Advance ¼ sol</button>
                <button disabled={busy} onClick={() => onAdvance(4)}>Run 1 habitat sol</button></div>}
        <div className="habitat-stock">{Object.entries(resources).map(([key, label]) => {
            const remaining = state.remaining[key];
            const initial = state.initial[key];
            return <div key={key}><span>{label}</span><strong>{remaining.toLocaleString(undefined, {maximumFractionDigits: 1})}</strong>
                <meter min={0} max={initial} low={initial * state.reserve} value={remaining}
                    aria-label={label + ' remaining'}/></div>;
        })}</div>
        {reading && <section className="habitat-live">
            <h4>Simulated field readings · {Math.round(reading.progress*100)}%</h4>
            {reading.ambient_temperature_c != null && <p>{reading.ambient_temperature_c} °C simulated ambient
                 {reading.equipment_active?.length ? ' · Active: '+reading.equipment_active.map((key:string)=>equipmentLabels[key]).join(', ') : ''}</p>}
            <p>Crew grid {reading.crew_grid.map((value: number) => value.toFixed(2)).join(' / ')} 
                {reading.near_reserve.length > 0 && <strong> · Near reserve: {reading.near_reserve.map((key: string) => resources[key]).join(', ')}</strong>}</p>
            <table><thead><tr><th>Resource</th><th>Used</th><th>Projected stock</th>{reading.crew_pack && <th>EVA pack</th>}</tr></thead>
                <tbody>{Object.entries(resources).map(([key,label]) => <tr key={key}><td>{label}</td>
                    <td>{reading.spent[key].toFixed(1)}</td><td>{reading.remaining[key].toFixed(1)}</td>{reading.crew_pack && <td>{reading.crew_pack[key]?.toFixed(1) ?? "—"}</td>}</tr>)}</tbody>
            </table>
        </section>}
        {plan && <details open={!plan.recorded}>
            <summary>{plan.recorded ? 'Recorded expedition '+plan.expedition : plan.started ? 'Expedition in progress' : plan.rejections.length ? 'Preflight held' : 'Preflight ready'}</summary>
            {plan.gear && <p>{plan.gear.label} · {plan.gear.temperature_c} °C assumed<br/>
                Active equipment: {plan.gear.active.map((key:string)=>equipmentLabels[key]).join(', ') || 'none'}
                {' · '}{plan.gear.gear_kg.toFixed(1)} kg carried · {plan.gear.extra_suit_wh_per_min.toFixed(1)} extra Wh/min.</p>}
            {!plan.recorded && <details className="preflight-advice">
                <summary>Mission Q&amp;A</summary>
                <form onSubmit={e=>{e.preventDefault(); if (question.trim().length>=3) onBriefing(question.trim());}}>
                    <label>Ask about this plan
                        <input value={question} maxLength={250} onChange={e=>setQuestion(e.target.value)}
                            placeholder="Why was this route chosen?"/>
                    </label>
                    <button disabled={briefingBusy || question.trim().length<3}>{briefingBusy ? 'Checking…' : 'Ask'}</button>
                </form>
                <div className="export-row">{['What equipment should I pack?', 'Why is preflight held?', 'How much oxygen will we use?'].map(prompt=>
                    <button key={prompt} disabled={briefingBusy} onClick={()=>{setQuestion(prompt);onBriefing(prompt);}}>{prompt}</button>)}</div>
                {briefing?.advice && <p role="status">{briefing.advice}</p>}
            </details>}
            {!plan.recorded && !plan.started && !plan.rejections.length && <button disabled={busy} onClick={onLaunch}>Start expedition</button>}
            <p>{plan.budget_reason} · {plan.effective_budget} min planned budget</p>
            <ul>{Object.entries(resources).filter(([key]) => plan.cost[key] > 0).map(([key, label]) =>
                <li key={key}>{label}: {plan.cost[key].toLocaleString(undefined, {maximumFractionDigits: 1})}</li>)}</ul>
            {plan.rejections.length > 0 && <ul role="alert">{plan.rejections.map((reason: string) => <li key={reason}>{reason}</li>)}</ul>}
            {!plan.recorded && plan.started && <p>{progress < 1 ? 'This expedition saves automatically when playback finishes.' : busy ? 'Saving expedition…' : 'Playback reached the end. Replay from an earlier point to finish automatically.'}</p>}
            {!plan.recorded && saveFailed && <button disabled={busy} onClick={onRecord}>Retry saving expedition</button>}
        </details>}
        {run?.decision_audit && <details>
            <summary>Why routes were passed over</summary>
            {run.decision_audit.coverage_checks && <p>Cells screened out of EVA: {run.decision_audit.coverage_checks.eva_slope_excluded} slope,
                {' '}{run.decision_audit.coverage_checks.eva_risk_excluded} risk,
                {' '}{run.decision_audit.coverage_checks.eva_disconnected} no connected path.</p>}
            <p>Previewed alternatives appear in purple. <button onClick={() => onPreview(null)}>Clear preview</button></p>
            <ul>{[...(run.decision_audit.route_candidates ?? []), ...(run.decision_audit.rejected_routes ?? [])].map((candidate: any, index: number) =>
                <li key={index}>{candidate.selected ? 'Selected · ' : ''}{candidate.target ? 'Grid ' + candidate.target.map((v: number) => v.toFixed(1)).join('/') + ' · ' : ''}
                    {candidate.distance_m != null ? candidate.distance_m + ' m · ' : ''}{candidate.reason}{candidate.ranking_score != null ? ' · score ' + candidate.ranking_score + ' · tail loss ' + Number(candidate.tail_loss).toFixed(3) : ''}
                    {candidate.path?.length > 1 && <button onClick={() => onPreview(candidate.path)}>Preview route {index+1}</button>}</li>)}</ul>
            {(run.sites ?? []).filter((site: any) => site.visit_fraction == null).map((site: any) =>
                <p key={site.id}>{site.label} · {site.status}</p>)}
            <small>Dijkstra searches eligible mesh edges. The planner favors more reachable stops, then compares simulated tail risk and distance.</small>
        </details>}
        {plan?.advice && <details><summary>Decision assistant · offline rules</summary>
            <p><strong>{plan.advice.action}</strong> · {plan.advice.detail}</p>
            {plan.advice.comparison && <p>{plan.advice.comparison}</p>}
            <p>{plan.budget_reason}. {plan.advice.next_step}</p>
        </details>}
        {state.history.length > 0 && <label>Campaign replay <select value="" disabled={busy} onChange={e => onReplay(e.target.value)}>
            <option value="" disabled>Select expedition</option>
            {state.history.map((entry: any, index: number) => <option key={entry.id} value={entry.id}>
                {index + 1} · {entry.objective} · {entry.condition}
            </option>)}
        </select></label>}
    </section>;
}
