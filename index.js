let wordList = [];
let checkBoxList = [];

function copyToClipboard(text) {
  var dummy = document.createElement("textarea");
  document.body.appendChild(dummy);
  dummy.value = text;
  dummy.select();
  document.execCommand("copy");
  document.body.removeChild(dummy);
}

document.getElementById("paste-area").onchange = function (event) {
  wordList = event.target.value.split(",");
  wordList = wordList.map((x) => x.trim());
  wordList.sort();

  const tableRoot = document.getElementById("table-root");
  while (tableRoot.firstChild) {
    tableRoot.removeChild(tableRoot.firstChild);
  }
  checkBoxList = [];
  document.getElementById("additions").value = "";
  document.getElementById("success-text").hidden = true;

  for (const word of wordList) {
    const tableRow = document.createElement("tr");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.id = word;
    checkbox.value = word;
    checkbox.checked = false;

    var label = document.createElement("label");
    label.htmlFor = word;
    label.appendChild(document.createTextNode(word));

    tableRow.appendChild(checkbox);
    tableRow.appendChild(label);
    tableRoot.appendChild(tableRow);
    checkBoxList.push(checkbox);
  }
};

// document.getElementById("submit-btn").onclick = function () {
//   let outputStr = "";
//   for (let i = 0; i < wordList.length; i++) {
//     if (checkBoxList[i].checked) {
//       outputStr += wordList[i] + "\n";
//     }
//   }

//   for (extraWord of document.getElementById("additions").value.split("\n")) {
//     outputStr += extraWord + "\n";
//   }

//   copyToClipboard(outputStr);
//   document.getElementById("success-text").hidden = false;
// };
