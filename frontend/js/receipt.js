(function () {
  'use strict';

  function handleBack(e) {
    if (e && e.preventDefault) {
      e.preventDefault();
    }
    var backBtn = document.getElementById('btn-back');
    var fallbackUrl = (backBtn && backBtn.getAttribute('href')) || '/';

    // 1. If user navigated inside the same tab from our site, go back in history
    if (window.history && window.history.length > 1 && document.referrer) {
      try {
        var refUrl = new URL(document.referrer);
        if (refUrl.origin === window.location.origin || refUrl.hostname.indexOf('vidhimeet') !== -1) {
          window.history.back();
          return;
        }
      } catch (err) {}
    }

    // 2. If referrer is a known VidhiMeet frontend origin (e.g. cross-origin backend vs frontend)
    if (document.referrer) {
      try {
        var refUrl2 = new URL(document.referrer);
        if (refUrl2.hostname.indexOf('vidhimeet') !== -1) {
          window.location.href = document.referrer;
          return;
        }
      } catch (err) {}
    }

    // 3. If opened via window.open() or script opener in a new tab/window, attempt closing tab
    if (window.opener && !window.opener.closed) {
      window.close();
      setTimeout(function () {
        window.location.href = fallbackUrl;
      }, 200);
      return;
    }

    // 4. Default fallback: navigate to homepage / portal
    window.location.href = fallbackUrl;
  }

  function getDocumentTitle() {
    var h1 = document.querySelector('.invoice-meta h1, .voucher-meta h3');
    var numEl = document.querySelector('.invoice-meta .meta-row span, .voucher-meta p span');
    var docName = (h1 && h1.textContent.trim()) || 'VidhiMeet';
    var docNum = (numEl && numEl.textContent.trim()) || 'Document';
    return (docName + '-' + docNum).replace(/[^a-zA-Z0-9_-]/g, '_');
  }

  var html2pdfLoading = false;
  var html2pdfLoaded = false;
  var html2pdfCallbacks = [];

  function loadHtml2PdfLazy(onSuccess, onError) {
    if (typeof html2pdf === 'function' || html2pdfLoaded) {
      if (onSuccess) onSuccess();
      return;
    }

    if (onSuccess) html2pdfCallbacks.push({ success: onSuccess, error: onError });

    if (html2pdfLoading) return;
    html2pdfLoading = true;

    var script = document.createElement('script');
    script.src = '/js/html2pdf.bundle.min.js';
    script.async = true;
    script.onload = function () {
      html2pdfLoaded = true;
      html2pdfLoading = false;
      var cbs = html2pdfCallbacks.slice();
      html2pdfCallbacks = [];
      cbs.forEach(function (cb) {
        if (cb.success) cb.success();
      });
    };
    script.onerror = function (err) {
      html2pdfLoading = false;
      var cbs = html2pdfCallbacks.slice();
      html2pdfCallbacks = [];
      cbs.forEach(function (cb) {
        if (cb.error) cb.error(err);
      });
    };
    document.head.appendChild(script);
  }

  function handleSavePdf(e) {
    if (e && e.preventDefault) {
      e.preventDefault();
    }
    var saveBtn = document.getElementById('btn-save-pdf') || document.getElementById('btn-print');
    var card = document.querySelector('.invoice-card, .card');

    if (!card) {
      tryPrint(e);
      return;
    }

    var originalText = saveBtn ? saveBtn.innerHTML : '';
    if (saveBtn) {
      saveBtn.innerHTML = '⏳ Generating PDF...';
      saveBtn.disabled = true;
    }

    function resetBtn() {
      if (saveBtn) {
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
      }
    }

    loadHtml2PdfLazy(function () {
      var filename = getDocumentTitle() + '.pdf';
      var opt = {
        margin: [6, 6, 6, 6],
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };

      html2pdf().set(opt).from(card).save().then(function () {
        resetBtn();
      }).catch(function (err) {
        console.warn('html2pdf generation error, falling back to window.print', err);
        resetBtn();
        tryPrint(e);
      });
    }, function (err) {
      console.warn('Failed to lazy load html2pdf, falling back to window.print', err);
      resetBtn();
      tryPrint(e);
    });
  }

  function tryPrint(e) {
    if (e && e.preventDefault) {
      e.preventDefault();
    }
    try {
      if (typeof window.print === 'function') {
        window.print();
      } else {
        handleSavePdf(e);
      }
    } catch (err) {
      console.warn('window.print error:', err);
      handleSavePdf(e);
    }
  }

  function initReceipt() {
    var backBtn = document.getElementById('btn-back');
    if (backBtn) {
      backBtn.addEventListener('click', handleBack);
    }

    var savePdfBtn = document.getElementById('btn-save-pdf');
    if (savePdfBtn) {
      savePdfBtn.addEventListener('click', handleSavePdf);
    }

    var printBtn = document.getElementById('btn-print');
    if (printBtn) {
      printBtn.addEventListener('click', tryPrint);
    }

    // Lazy load html2pdf in idle time so clicking 'Save as PDF' is instantaneous
    if ('requestIdleCallback' in window) {
      window.requestIdleCallback(function () {
        loadHtml2PdfLazy(null, null);
      }, { timeout: 3000 });
    } else {
      setTimeout(function () {
        loadHtml2PdfLazy(null, null);
      }, 2000);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReceipt);
  } else {
    initReceipt();
  }
})();
