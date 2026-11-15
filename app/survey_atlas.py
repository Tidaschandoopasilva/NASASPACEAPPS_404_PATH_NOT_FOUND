"""Convert a recorded survey to a compact campaign sector overlay."""

SECTORS = 16


def summarize(report):
    width, height = 226, 209
    readings = report.get("hazard_updated") or report["hazard"]
    if len(readings) != width * height:
        return {}
    def sector(point):
        row, col = point
        return min(SECTORS-1, int(row*SECTORS/95)), min(SECTORS-1, int(col*SECTORS/95))
    visited = {sector(site["cell"]) for site in report["sites"]
               if site["kind"] in ("EVA","ROVER") and site["visit_fraction"] is not None}
    pending = {sector(site["cell"]) for site in report["sites"]
               if site["visit_fraction"] is None or site["kind"] == "UAV"}
    closure = report.get("monitor_change_cell")
    closed_sector = sector(closure) if closure is not None else None
    output = {}
    for row in range(SECTORS):
        for col in range(SECTORS):
            y0, y1 = row*height//SECTORS, (row+1)*height//SECTORS
            x0, x1 = col*width//SECTORS, (col+1)*width//SECTORS
            samples = [(i,j,readings[i*width+j]) for i in range(y0,y1) for j in range(x0,x1)
                       if readings[i*width+j]>=0]
            if not samples:
                continue
            coverage = len(samples)/((y1-y0)*(x1-x0))
            blocked = sum(value>=68 for _,_,value in samples)/len(samples)
            peak = max(samples,key=lambda cell:cell[2])
            key = (row,col)
            if blocked>=.20 or key==closed_sector:
                outcome, reason = "hazard", "Recorded route closure" if key==closed_sector else "At least 20% of surveyed cells are EVA-excluded"
            elif key in pending or coverage<.35 or peak[2]>=68:
                outcome, reason = "revisit", "Pending target, partial coverage or isolated exclusion"
            elif key in visited:
                outcome, reason = "completed", "Recorded ground science stop inside sector"
            else:
                outcome, reason = "clear", "Surveyed with no exclusion in the modeled cells"
            output[f'{row}:{col}'] = {"row":row,"col":col,"status":outcome,"reason":reason,
                "coverage_pct":round(coverage*100),"excluded_pct":round(blocked*100),
                "peak_risk":peak[2],"peak_cell":[peak[0]*95/(height-1),peak[1]*95/(width-1)]}
    return output
