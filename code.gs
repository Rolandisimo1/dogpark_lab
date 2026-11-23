/**
 * PackTrack backend — Google Apps Script
 * Receives records from packtrack.html and stores them in this spreadsheet.
 * Setup: see SETUP.md (paste into a Sheet's Apps Script editor, run setup(),
 * deploy as a web app with access "Anyone", paste the web app URL into
 * packtrack.html).
 */

/** ARCHIVE SWITCH.
 *  false = normal: phones can add and delete records.
 *  true  = frozen: the web app still SERVES the data so the page can display
 *          results, but refuses every write, from any source. Changing this
 *          requires a NEW DEPLOYMENT VERSION to take effect (Deploy ->
 *          Manage deployments -> pencil -> Version: New version -> Deploy).
 *          Saving the file alone does nothing to the live endpoint. */
var LOCKED = false;

var TABLES = {
  dogs:   ["id","name","size","sex","age","coat","photoUrl","observer","epoch_ms","timestamp","received"],
  shakes: ["id","dogId","unregSize","type","pre","post","tailPre","tailPost","nearPre","nearPost","contact","observer","epoch_ms","timestamp","received"],
  focals: ["id","dogId","unregSize","b0","b20","shookDuring","observer","epoch_ms","timestamp","received"],
  gates:  ["id","dogId","unregSize","shook","latencySec","greeters","observer","epoch_ms","timestamp","received"]
};

/** Run this once by hand after pasting the code. Creates the four data tabs
 *  and a Drive folder for dog photos. */
function setup() {
  var ss = SpreadsheetApp.getActive();
  Object.keys(TABLES).forEach(function (name) {
    var sh = ss.getSheetByName(name) || ss.insertSheet(name);
    if (sh.getLastRow() === 0) sh.appendRow(TABLES[name]);
  });
  var props = PropertiesService.getScriptProperties();
  if (!props.getProperty("photoFolderId")) {
    var f = DriveApp.createFolder("PackTrack dog photos");
    props.setProperty("photoFolderId", f.getId());
  }
}

/** Wipe all four data tabs. For throwing away your own test records before
 *  class. Headers are kept. Dog photos stay in Drive; delete that folder by
 *  hand if you want them gone too. Run from the Apps Script editor. */
function clearTestData() {
  var ss = SpreadsheetApp.getActive(), n = 0;
  Object.keys(TABLES).forEach(function (name) {
    var sh = ss.getSheetByName(name);
    if (sh && sh.getLastRow() > 1) {
      n += sh.getLastRow() - 1;
      sh.deleteRows(2, sh.getLastRow() - 1);
    }
  });
  SpreadsheetApp.getActive().toast(n + " rows deleted. Tabs are empty and ready.");
  return n + " rows deleted";
}

/** Move the current records into archive tabs, then clear the live tabs.
 *  Use this between class sections so each section starts clean while the
 *  data accumulates for a pooled analysis. Run from the Apps Script editor. */
function archiveSection() {
  var ss = SpreadsheetApp.getActive();
  var label = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm");
  var moved = 0;
  Object.keys(TABLES).forEach(function (name) {
    var sh = ss.getSheetByName(name);
    if (!sh || sh.getLastRow() < 2) return;
    var cols = TABLES[name];
    var rows = sh.getRange(2, 1, sh.getLastRow() - 1, cols.length).getValues();
    var arch = ss.getSheetByName(name + "_archive");
    if (!arch) {
      arch = ss.insertSheet(name + "_archive");
      arch.appendRow(["session"].concat(cols));
    }
    var stamped = rows.map(function (r) { return [label].concat(r); });
    arch.getRange(arch.getLastRow() + 1, 1, stamped.length, cols.length + 1).setValues(stamped);
    sh.deleteRows(2, sh.getLastRow() - 1);
    moved += stamped.length;
  });
  SpreadsheetApp.getActive().toast(moved + " rows archived as \"" + label + "\". Live tabs are clear.");
  return moved + " rows archived";
}

function doGet(e) {
  var mode = (e && e.parameter && e.parameter.mode) || "";
  if (mode === "data") return jsonOut(allData());
  return jsonOut({ ok: true, service: "PackTrack", time: new Date().toISOString() });
}

function doPost(e) {
  if (LOCKED) {
    return jsonOut({ ok: false,
      error: "This study is archived. The dataset is closed and no longer accepting records." });
  }
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var b = JSON.parse(e.postData.contents);
    if (b.action === "add" || b.action === "addDog") {
      var table = b.action === "addDog" ? "dogs" : String(b.table);
      if (!TABLES[table]) return jsonOut({ ok: false, error: "unknown table" });
      var row = b.row || {};
      if (b.action === "addDog" && b.photo) {
        try { row.photoUrl = savePhoto(b.photo, row.id); }
        catch (err) { row.photoUrl = ""; }
      }
      row.received = new Date().toISOString();
      upsert(table, row);
      return jsonOut({ ok: true, photoUrl: row.photoUrl || null });
    }
    if (b.action === "delete") {
      if (!TABLES[b.table]) return jsonOut({ ok: false, error: "unknown table" });
      removeRow(String(b.table), String(b.id));
      return jsonOut({ ok: true });
    }
    return jsonOut({ ok: false, error: "unknown action" });
  } catch (err) {
    return jsonOut({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

/* ---------- helpers ---------- */

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function sheet(name) {
  return SpreadsheetApp.getActive().getSheetByName(name);
}

/** Insert a row keyed by its "id"; if the id already exists, replace that row
 *  (this is how a dog's details get edited). Keeps an existing photoUrl when
 *  the update carries none. */
function upsert(table, row) {
  var sh = sheet(table), cols = TABLES[table];
  var last = sh.getLastRow();
  var idx = -1, oldVals = null;
  if (last > 1) {
    var ids = sh.getRange(2, 1, last - 1, 1).getValues();
    for (var i = 0; i < ids.length; i++) {
      if (String(ids[i][0]) === String(row.id)) { idx = i + 2; break; }
    }
  }
  if (idx > 0 && (row.photoUrl === undefined || row.photoUrl === "" || row.photoUrl === null)) {
    oldVals = sh.getRange(idx, 1, 1, cols.length).getValues()[0];
    var pCol = cols.indexOf("photoUrl");
    if (pCol >= 0) row.photoUrl = oldVals[pCol];
  }
  var vals = cols.map(function (c) { return row[c] === undefined || row[c] === null ? "" : row[c]; });
  if (idx > 0) sh.getRange(idx, 1, 1, cols.length).setValues([vals]);
  else sh.appendRow(vals);
}

function removeRow(table, id) {
  var sh = sheet(table), last = sh.getLastRow();
  if (last < 2) return;
  var ids = sh.getRange(2, 1, last - 1, 1).getValues();
  for (var i = ids.length - 1; i >= 0; i--) {
    if (String(ids[i][0]) === String(id)) { sh.deleteRow(i + 2); return; }
  }
}

/** Save a data-URI JPEG to the photos folder, share it by link, and return a
 *  thumbnail URL the web page can use in an <img>. */
function savePhoto(dataUri, id) {
  var m = dataUri.match(/^data:(image\/\w+);base64,(.+)$/);
  if (!m) return "";
  var blob = Utilities.newBlob(Utilities.base64Decode(m[2]), m[1], "dog-" + id + ".jpg");
  var folderId = PropertiesService.getScriptProperties().getProperty("photoFolderId");
  var folder = folderId ? DriveApp.getFolderById(folderId) : DriveApp.getRootFolder();
  var file = folder.createFile(blob);
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  return "https://drive.google.com/thumbnail?id=" + file.getId() + "&sz=w240";
}

function allData() {
  var out = { ok: true, time: new Date().toISOString() };
  Object.keys(TABLES).forEach(function (name) {
    var sh = sheet(name), cols = TABLES[name], rows = [];
    if (sh && sh.getLastRow() > 1) {
      var vals = sh.getRange(2, 1, sh.getLastRow() - 1, cols.length).getValues();
      rows = vals.map(function (v) {
        var o = {};
        cols.forEach(function (c, i) { o[c] = v[i] === "" ? null : v[i]; });
        return o;
      });
    }
    out[name] = rows;
  });
  return out;
}
