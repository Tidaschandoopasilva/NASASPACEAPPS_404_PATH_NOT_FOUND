export const equipmentLabels: Record<string,string> = {
    heater: 'Suit heater', cooler: 'Cooling pack', visibility: 'Navigation beacon',
};
export const conditionInfo: Record<string,{temperature:number; gear?:string}> = {
    day: {temperature:-20}, night: {temperature:-75,gear:'heater'},
    heat: {temperature:8,gear:'cooler'}, dust: {temperature:-35,gear:'visibility'},
};
export const sectorStyles: Record<string,{label:string; stroke:string; fill:string}> = {
    completed:{label:'Expedition completed',stroke:'#7dd3fc',fill:'#1471aa70'},
    clear:{label:'Modeled passable',stroke:'#86efac',fill:'#15803d70'},
    hazard:{label:'EVA exclusion',stroke:'#fca5a5',fill:'#9f123990'},
    revisit:{label:'Requires re-expedition',stroke:'#fcd34d',fill:'#a162077f'},
};
