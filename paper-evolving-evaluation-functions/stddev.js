const fs = require('fs');

const resultPattern = /^\s*(\S+)\s*(\S+)\s*wins=\s*(\d+\.\d+)%\s*errs=\s*(\d+\.\d+)%\s*alls=\s*(\d+)$/;
const averages = {};

function normalize(name) {
  // return name.includes('-frombest') ? name.slice(0, -2) : name;
  return (
    name[name.length - 4] === '-' ? name.slice(0, -4) :
    name[name.length - 2] === '-' ? name.slice(0, -2) :
    name
  );
}

function pad(x) {
  return `${x.padStart(50 + 1)} `;
}

function wrap(agent) {
  return `\\texttt{${agent}}`;
}

function stats(array) {
  const avg = array.reduce((sum, x) => sum + x, 0) / array.length;
  const stddev = Math.sqrt(array.reduce((sum, x) => sum + Math.pow(x - avg, 2), 0) / array.length);
  return ` ${avg.toFixed(2).padStart(5)}$\\pm$${stddev.toFixed(2)}\\%`.padEnd(50);
}

fs
  .readFileSync('./graph.data', 'utf-8')
  .split('\n')
  .map(line => resultPattern.exec(line))
  .filter(Boolean)
  .forEach(([, agentA, agentB, wins, errs, alls]) => {
    ((averages[normalize(agentA)] ??= {})[normalize(agentB)] ??= []).push(+wins);
  });

const agents = Object.keys(averages).sort();
console.log(['', ...agents.map(wrap), 'average'].map(pad).join('&'));
for (const agentA of agents) {
  console.log([
    wrap(agentA),
    ...agents.map(agentB => agentA === agentB ? ' --'.padEnd(50) : stats(averages[agentA][agentB])),
    stats(agents.flatMap(agentB => agentA === agentB ? [] : averages[agentA][agentB])),
  ].map(pad).join('&'));
}
