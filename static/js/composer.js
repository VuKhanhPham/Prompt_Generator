// Make currentScore globally accessible so library.js can update it
var currentScore = {};

$(function () {
  // ---------- helpers ----------

  function toneLabel(v) {
    const value = Number(v);
    if (value < 25) return "Formal";
    if (value < 60) return "Friendly";
    return "Witty";
  }

  function updateScoreUI(score) {
    if (!score || !score.details) {
      $("#score-details").html("");
      return;
    }
    const d = score.details;
    $("#score-details").html(
      `
      <strong>Total score: ${score.total}</strong><br>
      <span>Clarity: ${d.clarity}</span> ·
      <span>Specificity: ${d.specificity}</span> ·
      <span>Tone match: ${d.tone_match}</span> ·
      <span>Length bonus: ${d.length_bonus}</span>
      `
    );
  }

  function showMessage(text) {
    $("#composer-message").text(text).fadeIn(150).delay(1200).fadeOut(200);
  }

  // ---------- initial tone label ----------

  $("#tone-label").text(toneLabel($("#tone").val() || 40));

  // ---------- events ----------

  // Tone slider label
  $("#tone").on("input", function () {
    $("#tone-label").text(toneLabel($(this).val()));
  });

  // Compose Prompt
  $("#compose-btn").click(function () {
    const payload = {
      purpose: $("#purpose").val(),
      audience: $("#audience").val(),
      tone_label: toneLabel($("#tone").val()),
      tone: Number($("#tone").val()),
      keywords: $("#keywords").val(),
      freeform: $("#freeform").val(),
    };

    if (!payload.purpose.trim()) {
      showMessage("Please enter a purpose before composing.");
      return;
    }

    $.ajax({
      url: "/compose",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function (res) {
        $("#preview").val(res.prompt);
        currentScore = res.score || {};
        updateScoreUI(currentScore);
        showMessage("Prompt composed.");
      },
      error: function () {
        showMessage("Error composing prompt.");
      },
    });
  });

  // Save to Library
  $("#save-btn").click(function () {
    const payload = {
      purpose: $("#purpose").val(),
      audience: $("#audience").val(),
      tone_label: toneLabel($("#tone").val()),
      tone: Number($("#tone").val()),
      keywords: $("#keywords").val(),
      freeform: $("#freeform").val(),
      prompt: $("#preview").val(),
      score: currentScore,
    };

    if (!payload.prompt.trim()) {
      showMessage("Compose a prompt before saving.");
      return;
    }

    $.ajax({
      url: "/save",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function () {
        showMessage("Prompt saved to library.");
      },
      error: function () {
        showMessage("Error saving prompt.");
      },
    });
  });

  // Recalculate Score after manual edits
  $("#recalc-btn").click(function () {
    const newText = $("#preview").val();
    if (!newText.trim()) {
      showMessage("There is no prompt text to score.");
      return;
    }

    $.ajax({
      url: "/recalculate_score",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        prompt: newText,
        input_keywords: $("#keywords").val(),
        freeform_input: $("#freeform").val(),
      }),
      success: function (score) {
        currentScore = score || {};
        updateScoreUI(currentScore);
        showMessage("Score updated.");
      },
      error: function () {
        showMessage("Error recalculating score.");
      },
    });
  });
});
