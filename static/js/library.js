$(function(){
  function loadLibrary(){
    $.get("/library", function(res){ renderList(res); });
  }
  function renderList(list){
    const $lib = $("#library-list");
    $lib.empty();
    if(!list.length){ $lib.text("No prompts yet."); return; }
    list.slice().reverse().forEach(it=>{
      // Card display with purpose, audience, tone, keywords, score, and prompt preview
      const card = $(`<div class='border rounded p-2 mb-2 library-item' style='cursor:pointer;'><strong>${it.purpose}</strong><div class='small text-muted'>Audience: ${it.audience || '—'}</div><div class='small text-muted'>Tone: ${it.tone_label || '—'}</div><div class='small text-muted'>Keywords: ${it.keywords || '—'}</div><div class='small'>Score: ${(it.score?.total)||'—'}</div><div class='mt-1 small text-secondary'>${(it.prompt || '').slice(0,100)}...</div></div>`);
      card.click(function(){
        // Fill all composer fields
        $("#purpose").val(it.purpose);
        $("#audience").val(it.audience || "");
        $("#tone").val(it.tone || 40);
        $("#tone-label").text(it.tone_label || "Friendly");
        $("#keywords").val(it.keywords || "");
        $("#freeform").val(it.freeform || "");
        $("#preview").val(it.prompt || "");
        
        // Update score display to match composer format
        if (it.score && it.score.details) {
          const d = it.score.details;
          $("#score-details").html(
            `<strong>Total score: ${it.score.total}</strong><br>
             <span>Clarity: ${d.clarity||0}</span> ·
             <span>Specificity: ${d.specificity||0}</span> ·
             <span>Tone match: ${d.tone_match||0}</span> ·
             <span>Length bonus: ${d.length_bonus||0}</span>`
          );
          // Update currentScore so it's available when saving
          if (typeof currentScore !== 'undefined') {
            currentScore = it.score;
          }
          // Also set on window to ensure it's accessible
          window.currentScore = it.score;
        } else {
          $("#score-details").html("");
          if (typeof currentScore !== 'undefined') {
            currentScore = {};
          }
        }
        $('html, body').animate({ scrollTop: $("#compose-btn").offset().top - 100 }, 400);
      });
      $lib.append(card);
    });
  }
  $("#search-btn").click(function(){
    const kw = $("#search-key").val();
    $.ajax({
      url: "/library/search",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({keyword: kw}),
      success: renderList
    });
  });
  $("#sortAZ-btn").click(function(){
    const kw = $("#search-key").val();
    $.ajax({
      url: "/library/sortAZ",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({keyword: kw}),
      success: renderList
    });
  });
  $("#sortScore-btn").click(function(){
    const kw = $("#search-key").val();
    $.ajax({
      url: "/library/sortScore",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({keyword: kw}),
      success: renderList
    });
  });
  $("#sortTone-btn").click(function(){
    const kw = $("#search-key").val();
    $.ajax({
      url: "/library/sortTone",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({keyword: kw}),
      success: renderList
    });
  });
  loadLibrary();
});