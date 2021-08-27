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

function onPasteAreaChange(event) {
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
}
var area = document.getElementById("paste-area");
if (area.addEventListener) {
  area.addEventListener("input", onPasteAreaChange, false);
} else if (area.attachEvent) {
  area.attachEvent("onpropertychange", onPasteAreaChange);
}

document.getElementById("submit-btn").onclick = function () {
  let outputStr = "";
  for (let i = 0; i < wordList.length; i++) {
    if (checkBoxList[i].checked && wordList[i]) {
      outputStr += wordList[i] + ";";
    }
  }

  for (extraWord of document.getElementById("additions").value.split(/,|\n/g)) {
    outputStr += extraWord.trim() + ";";
  }

  copyToClipboard(outputStr);
  document.getElementById("success-text").hidden = false;
  setTimeout(() => {
    document.getElementById("success-text").hidden = true;
  }, 2000);
};
