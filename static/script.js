// summonerName: [level, tier, rank, lp, mmr, lpdelta, wins, losses]

const tableBody = document.getElementById('leaderboard-body');

let currentSort = {
  by: '', // 'rank' | 'name'
  direction: '' // 'asc' | 'desc'
};

/**
 * @param {'mmr' | 'level' | 'wins' | 'losses' | 'lpdelta' | 'dailywins' | 'yesterday'} by
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
  numbering();
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
  numbering();
};

sortNum('mmr');

function search() {
  // Declare variables
  var input, filter, table, table2, tr, tr2, td, i, txtValue;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("leaderboard");
  tr = table.getElementsByTagName("tr");
  table2 = document.getElementById("rnk");
  tr2 = table2.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
        tr2[i].style.display = "";
      } else {
        tr[i].style.display = "none";
        tr2[i].style.display = "none";
      }
    }
  }
}

function colorToday() {
  var table, tr, td, i, lpDelta;
  table = document.getElementById("leaderboard");
  tr = table.getElementsByTagName("tr");

  for(i=0; i< tr.length; i++) {
    deltaLP = tr[i].getElementsByTagName("td")[8];
    dailyGames = tr[i].getElementsByTagName("td")[9];
    // console.log(td) = lpdelta value per row
    if(deltaLP) {
      if(deltaLP.innerHTML < 0) {
        deltaLP.style.backgroundColor = "red"
      } else if (deltaLP.innerHTML > 0) {
        deltaLP.style.backgroundColor = "green"
       } else if(deltaLP.innerHTML == 0 && dailyGames.innerHTML > 0){
        deltaLP.style.backgroundColor = "yellow"
       }
    }
  }
}
colorToday();

function colorYesterday() {
  var table, tr, td, i, lpDelta;
  table = document.getElementById("leaderboard");
  tr = table.getElementsByTagName("tr");

  for(i=0; i< tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[10];
    // console.log(td) = lpdelta value per row
    if(td) {
      if(td.innerHTML < 0) {
        td.style.backgroundColor = "red"
      } else if (td.innerHTML > 0) {
        td.style.backgroundColor = "green"
       } //else if (td.innerHTML == 0) {
         //td.style.backgroundColor = "yellow"
       //}
    }
  }
}
colorYesterday()

function numbering() {
  table = document.getElementById("leaderboard")
  tr = table.getElementsByTagName("tr")
  row = document.getElementsByClassName("num");
  var j = 1;
  for(i=0; i< tr.length; i++)
  {
    if(row[i] === undefined)
    {
      break;
    }
    row[i].innerHTML = j;
    j = j +1;
  }
}
//tets