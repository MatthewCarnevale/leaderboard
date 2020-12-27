// summonerName: [level, tier, rank, lp, mmr, lpdelta, wins, losses]
console.log('hello4')

const tableBody = document.getElementById('leaderboard-body');

let currentSort = {
  by: '', // 'rank' | 'name'
  direction: '' // 'asc' | 'desc'
};

/**
 * @param {'mmr' | 'level' | 'wins' | 'losses' | 'lpdelta'} by
 */
const sortNum = (by) => {
  const tempRows = Array.from(tableBody.childNodes).filter(row => !!row.dataset && !!row.dataset[by]);
  let rows;
  if (currentSort.direction === 'asc' && currentSort.by === by) {
    rows = tempRows.sort(
      (a, b) => (+a.dataset[by]) - (+b.dataset[by])
    );
    currentSort.direction = 'desc';
  } else {
    rows = tempRows.sort(
      (a, b) => (+b.dataset[by]) - (+a.dataset[by])
    );
    currentSort.direction = 'asc';
  }
  currentSort.by = by;
  rows.forEach((row) => tableBody.append(row));
};

/**
 * @param {'name'} by
 */
const sortAlpha = (by) => {
  const tempRows = Array.from(tableBody.childNodes).filter(row => !!row.dataset && !!row.dataset[by]);
  let rows;
  if (currentSort.direction === 'asc' && currentSort.by === by) {
    rows = tempRows.sort(
      (a, b) => a.dataset[by].localeCompare(b.dataset[by])
    );
    currentSort.direction = 'desc';
  } else {
    rows = tempRows.sort(
      (a, b) => b.dataset[by].localeCompare(a.dataset[by])
    );
    currentSort.direction = 'asc';
  }
  currentSort.by = by;
  rows.forEach((row) => tableBody.append(row));
};

sortNum('mmr');
