  var puzzleFailed = false;
  var puzzleStartTime = new Date();  // Czas rozpoczęcia puzzla

  // FEN cofniętej pozycji z Pythona
  var fenFromFlask = "{{ fen }}";

  // Pobranie game_url z szablonu Flask
  var gameUrl = "{{ game_url }}";

  // Wyodrębnienie części po znaku '#' oraz konwersja na liczbę całkowitą
  var lastPart = gameUrl.split('#').pop();
  var num = parseInt(lastPart, 10);

  // Ustalenie orientacji na podstawie parzystości numeru
  var boardOrientation = (num % 2 === 1) ? 'black' : 'white';

  // Inicjujemy chessboard.js
  var board = Chessboard('board', {
    pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
    position: fenFromFlask,
    draggable: false,
    orientation: boardOrientation
  });

  // JSON-ujemy listę ruchów z back-endu
  var solutionMovesJson = '{{ solutionMoves|tojson|safe }}';
var solutionMoves = JSON.parse(solutionMovesJson);
  console.log(solutionMoves);

  var currentIndex = 1;

  var ranks, files;
  if(boardOrientation === 'black'){
      ranks = [1,2,3,4,5,6,7,8];
      files = ['h','g','f','e','d','c','b','a'];
  } else {
      ranks = [8,7,6,5,4,3,2,1];
      files = ['a','b','c','d','e','f','g','h'];
  }

  var userBoardEl = document.getElementById("userBoard");
  userBoardEl.innerHTML = "";

  // Górny wiersz z etykietami plików
  var topRow = userBoardEl.insertRow();
  var emptyCell = topRow.insertCell();
  for(var f = 0; f < 8; f++){
      var cell = topRow.insertCell();
      cell.innerText = files[f];
      cell.style.textAlign = "center";
  }

  // Wiersze planszy z etykietami rang i kolorowaniem pól
  for (var r = 0; r < 8; r++) {
    var row = userBoardEl.insertRow();
    var rankLabelCell = row.insertCell();
    rankLabelCell.innerText = ranks[r];
    rankLabelCell.style.textAlign = "center";
    for (var c = 0; c < 8; c++) {
      var cell = row.insertCell();

      // Warunkowe określenie koloru pola
      // Standardowe określenie koloru pola, niezależnie od orientacji
var isDark = ((r + c) % 2 === 0);
cell.classList.add(isDark ? 'light' : 'dark');


      var sq = files[c] + ranks[r];
      cell.setAttribute('data-square', sq);
      cell.addEventListener('click', onCellClick);
    }
  }

  // Dolny wiersz z etykietami plików
  var bottomRow = userBoardEl.insertRow();
  var bottomEmpty = bottomRow.insertCell();
  for(var f = 0; f < 8; f++){
      var cell = bottomRow.insertCell();
      cell.innerText = files[f];
      cell.style.textAlign = "center";
  }

  var firstClick = null;
  var infoEl = document.getElementById("info");
  var messagesEl = document.getElementById("messages");

  function displayMessage(message) {
    messagesEl.innerHTML += "<p>" + message + "</p>";
  }

  function onCellClick(e) {
    var sq = e.target.getAttribute('data-square');
    if (!firstClick) {
      firstClick = sq;
      infoEl.innerText = "Źródło: " + sq;
    } else {
      var secondClick = sq;
      var userMove = firstClick + secondClick; // np. "g5g6"
      
      // Jeśli puzzle już ukończone:
      if (currentIndex >= solutionMoves.length) {
        displayMessage("Puzzle już jest ukończone!");
        resetClicks();
        return;
      }

      var expectedMove = solutionMoves[currentIndex];
      if (userMove === expectedMove) {
        displayMessage("Poprawny ruch: " + userMove);
        currentIndex++;

        // Ruch przeciwnika (jeśli jest i wypada w parzystym indexie)
        if (currentIndex < solutionMoves.length && (currentIndex % 2 === 0)) {
          var oppMove = solutionMoves[currentIndex];
          displayMessage("Ruch przeciwnika: " + oppMove);
          currentIndex++;
        }

        // Koniec puzzle?
        if (currentIndex >= solutionMoves.length) {
          displayMessage("Gratulacje, koniec puzzle!");
          board.position('{{ puzzle_fen }}', false);

          // Logika zapisu w przypadku sukcesu
          var puzzleEndTime = new Date();
          var solveTimeInSeconds = (puzzleEndTime - puzzleStartTime) / 1000;
var BlindMovesJson = '{{blind_moves|tojson|safe}}';
var BlindMoves = JSON.parse(BlindMovesJson)
          var successData = {
            PuzzleId: "{{ PuzzleId }}",
            SolveDate: new Date().toISOString(),
            SolveTime: solveTimeInSeconds,
            Result: 1,
            BlindMoves: BlindMoves,
          };

          fetch('/submit_result', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(successData)
          }).then(response => response.json())
            .then(respData => {
              console.log('Wynik zapisany:', respData);
            }).catch(err => {
              console.error('Błąd podczas zapisywania wyniku:', err);
            });
        }
      } else {
        displayMessage("Błędny ruch! Oczekiwano: " + expectedMove + ", wybrałeś: " + userMove);

        // Logika zapisu w przypadku błędu, tylko raz
        if (!puzzleFailed) {
          puzzleFailed = true;
          var puzzleEndTime = new Date();
          var solveTimeInSeconds = (puzzleEndTime - puzzleStartTime) / 1000;

          var failureData = {
            PuzzleId: "{{ PuzzleId }}",
            SolveDate: new Date().toISOString(),
            SolveTime: solveTimeInSeconds,
            Result: 0,
            BlindMoves: BlindMoves,
          };

          fetch('/submit_result', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(failureData)
          }).then(response => response.json())
            .then(respData => {
              console.log('Wynik zapisany (nieudany):', respData);
            }).catch(err => {
              console.error('Błąd podczas zapisywania wyniku:', err);
            });
        }

        disableBoard();
      }
      resetClicks();
    }
  }

  function resetClicks() {
    firstClick = null;
    infoEl.innerText = "";
  }

  function disableBoard() {
    var cells = userBoardEl.getElementsByTagName("td");
    for (var i = 0; i < cells.length; i++) {
      cells[i].removeEventListener('click', onCellClick);
    }
  }
