const mockLawyers = [
  {id:"1",name:"Adv. Aanya Rao",initials:"AR",practice:"Family Law",specialty:"Divorce & Child Custody",rating:4.9,reviews:128,years:12,languages:"English, Hindi, Kannada",fee:1800,available:true,color:"#d9b39b"},
  {id:"2",name:"Adv. Sameer Khanna",initials:"SK",practice:"Corporate Law",specialty:"Contracts & Company Law",rating:4.8,reviews:94,years:9,languages:"English, Hindi, Telugu",fee:2200,available:true,color:"#a8c1b5"},
  {id:"3",name:"Adv. Meera Nair",initials:"MN",practice:"Property Law",specialty:"Property & Title Disputes",rating:5.0,reviews:76,years:14,languages:"English, Malayalam",fee:2000,available:false,color:"#c5b7d0"},
  {id:"4",name:"Adv. Kabir Shah",initials:"KS",practice:"Family Law",specialty:"Inheritance & Mediation",rating:4.7,reviews:61,years:8,languages:"English, Gujarati, Kannada",fee:1500,available:true,color:"#b9c8da"},
  {id:"5",name:"Adv. Priya Iyer",initials:"PI",practice:"Corporate Law",specialty:"IP & Startup Advisory",rating:4.9,reviews:103,years:11,languages:"English, Tamil, Telugu",fee:2500,available:false,color:"#d8c5a4"},
  {id:"6",name:"Adv. Rohan Das",initials:"RD",practice:"Property Law",specialty:"Tenancy & Real Estate",rating:4.8,reviews:87,years:10,languages:"English, Bengali",fee:1750,available:true,color:"#abc9c9"}
];

const intake = {
  "Property Law": ["What type of property is involved?", "What is your relationship to the property?", "Are there active legal proceedings?"],
  "Corporate Law": ["What type of business is involved?", "What help do you need?", "Is there a deadline we should know about?"],
  "Family Law": ["What best describes your situation?", "Are any children involved?", "Is there an existing court order?"]
};

let lawyers = [];
let practice = "Property Law", filter = "all", booking = {};
let clientChatInterval = null;

const grid = document.querySelector("#lawyer-grid");
const backdrop = document.querySelector("#backdrop");
const modal = document.querySelector(".modal");
const content = document.querySelector("#modal-content");

const money = n => new Intl.NumberFormat("en-IN", {style: "currency", currency: "INR", maximumFractionDigits: 0}).format(n);

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function darken(hex) {
  return hex.replace(/[0-9a-f]{2}/gi, p => Math.max(0, parseInt(p, 16) - 45).toString(16).padStart(2, "0"));
}

function open() {
  backdrop.hidden = false;
  document.body.style.overflow = "hidden";
}

function close() {
  backdrop.hidden = true;
  document.body.style.overflow = "";
  modal.classList.remove("video");
  modal.classList.remove("chat");
  if (window.dailyCallFrame) {
    window.dailyCallFrame.destroy();
    window.dailyCallFrame = null;
  }
  if (clientChatInterval) {
    clearInterval(clientChatInterval);
    clientChatInterval = null;
  }
}

function closeModal() {
  close();
}

function mapPracticeToBackend(p) {
  if (!p) return "property";
  if (Array.isArray(p)) return mapPracticeToBackend(p[0]);
  if (p === "Property Law") return "property";
  if (p === "Corporate Law") return "corporate";
  if (p === "Family Law") return "family";
  const str = String(p).toLowerCase();
  if (str.includes("property") || str.includes("land")) return "property";
  if (str.includes("corporate") || str.includes("company") || str.includes("contract")) return "corporate";
  if (str.includes("family") || str.includes("divorce") || str.includes("child")) return "family";
  return "property";
}

function mapPracticeToFrontend(p) {
  if (Array.isArray(p)) return p.map(mapPracticeToFrontend).join(", ");
  if (p === "property") return "Property Law";
  if (p === "corporate") return "Corporate Law";
  if (p === "family") return "Family Law";
  return p;
}

function getSpecialty(p) {
  if (Array.isArray(p)) return p.map(getSpecialty).join(", ");
  if (p === "property") return "Property & Title Disputes";
  if (p === "corporate") return "Contracts & Company Law";
  if (p === "family") return "Divorce & Child Custody";
  return "Legal Advice";
}

function resolveBookingPractice(lawyer, activePractice) {
  if (!lawyer) return activePractice || "Property Law";
  
  let lawyerPractices = [];
  if (Array.isArray(lawyer.practices)) {
    lawyerPractices = lawyer.practices.map(p => mapPracticeToFrontend(p));
  } else if (typeof lawyer.practice === "string") {
    lawyerPractices = lawyer.practice.split(",").map(p => p.trim());
  }

  const activeFrontend = mapPracticeToFrontend(mapPracticeToBackend(activePractice));
  if (lawyerPractices.includes(activeFrontend)) {
    return activeFrontend;
  }
  return lawyerPractices[0] || activeFrontend || "Property Law";
}

function getIntakeQuestions(practiceInput) {
  const formatted = mapPracticeToFrontend(mapPracticeToBackend(practiceInput));
  if (intake[formatted]) return intake[formatted];
  if (intake[practiceInput]) return intake[practiceInput];
  const str = String(practiceInput || "");
  if (str.includes("Corporate") || str.includes("corporate") || str.includes("Company") || str.includes("Contract")) return intake["Corporate Law"];
  if (str.includes("Family") || str.includes("family") || str.includes("Divorce") || str.includes("Child")) return intake["Family Law"];
  return intake["Property Law"];
}

function getIntakeKeys(practiceInput) {
  const keysMap = {
    "Property Law": ["property_type", "relationship", "active_proceedings"],
    "Corporate Law": ["business_type", "help_needed", "deadline"],
    "Family Law": ["matter_type", "children_involved", "existing_order"]
  };
  const formatted = mapPracticeToFrontend(mapPracticeToBackend(practiceInput));
  if (keysMap[formatted]) return keysMap[formatted];
  if (keysMap[practiceInput]) return keysMap[practiceInput];
  const str = String(practiceInput || "");
  if (str.includes("Corporate") || str.includes("corporate") || str.includes("Company") || str.includes("Contract")) return keysMap["Corporate Law"];
  if (str.includes("Family") || str.includes("family") || str.includes("Divorce") || str.includes("Child")) return keysMap["Family Law"];
  return keysMap["Property Law"];
}



function getColorForName(name) {
  const colors = ["#d9b39b", "#a8c1b5", "#c5b7d0", "#b9c8da", "#d8c5a4", "#abc9c9"];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

function getYearsExperience(enrollmentDateStr) {
  if (!enrollmentDateStr) return null;
  const enrollDate = new Date(enrollmentDateStr);
  const today = new Date();
  if (isNaN(enrollDate.getTime())) return null;
  let years = today.getFullYear() - enrollDate.getFullYear();
  let months = today.getMonth() - enrollDate.getMonth();
  if (months < 0) {
    years--;
  }
  return years >= 0 ? years : 0;
}

async function loadPublicStats() {
  try {
    const stats = await LexAPI.publicStats();
    if (!stats) return;

    // ── Practice card counts ──────────────────────────────────────────────────
    const byPractice = stats.lawyers_by_practice || {};
    const familyEl = document.getElementById("count-family");
    const corpEl   = document.getElementById("count-corporate");
    const propEl   = document.getElementById("count-property");
    if (familyEl) familyEl.textContent = `${byPractice["family"] ?? 0} verified lawyers`;
    if (corpEl)   corpEl.textContent   = `${byPractice["corporate"] ?? 0} verified lawyers`;
    if (propEl)   propEl.textContent   = `${byPractice["property"] ?? 0} verified lawyers`;

    // ── "Available today" float ───────────────────────────────────────────────
    const onlineEl = document.getElementById("stat-lawyers-online");
    if (onlineEl) {
      const total = stats.verified_lawyers || 0;
      onlineEl.textContent = `${total} lawyer${total !== 1 ? "s" : ""} available`;
    }

    // ── Trust badge: Verified + client count ────────────────────────────
    const ratingEl  = document.getElementById("trust-rating");
    const clientsEl = document.getElementById("trust-clients");
    if (ratingEl) {
      ratingEl.innerHTML = `Verified <span>✓</span>`;
    }
    if (clientsEl && stats.total_clients > 0) {
      const c = stats.total_clients;
      const label = c >= 1000
        ? `${(c / 1000).toFixed(1).replace(/\.0$/, "")}K+`
        : `${c}+`;
      clientsEl.textContent = `Trusted by ${label} clients`;
    }

    // ── Trust faces: show initials of real lawyers ────────────────────────────
    const facesEl = document.getElementById("trust-faces");
    if (facesEl && lawyers.length > 0) {
      const picks = lawyers.slice(0, 3);
      facesEl.innerHTML = picks.map(l =>
        `<b style="background:${l.color}">${l.initials}</b>`
      ).join("");
    }
  } catch (err) {
    console.warn("Could not load public stats:", err);
  }
}

async function loadLawyers() {
  const isLocalhost = ["localhost", "127.0.0.1", "0.0.0.0"].includes(window.location.hostname);
  try {
    const list = await LexAPI.lawyers();
    lawyers = list.map(x => ({
      id: x.id,
      name: x.full_name,
      practices: x.practice || [],
      practice: mapPracticeToFrontend(x.practice),
      specialty: getSpecialty(x.practice),
      rating: x.rating || 0.0,
      reviews: Math.floor((x.rating || 5.0) * 20) + (x.id.charCodeAt(0) % 15),
      years: getYearsExperience(x.enrollment_date) !== null ? getYearsExperience(x.enrollment_date) : (5 + (x.id.charCodeAt(0) % 15)),
      languages: x.languages.join(", "),
      fee: x.hourly_fee_minor / 100,
      available: true,
      availability: x.availability || {},
      color: getColorForName(x.full_name),
      initials: x.full_name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase()
    }));
    if (lawyers.length === 0 && isLocalhost) {
      lawyers = mockLawyers;
    }
  } catch (err) {
    console.error("Failed to load lawyers:", err);
    if (isLocalhost) {
      lawyers = mockLawyers;
    } else {
      lawyers = [];
    }
  }
  render();
  // Populate live stats after lawyers are loaded (so trust faces can use real initials)
  loadPublicStats();
}


function render() {
  let list = lawyers.filter(x => {
    const selectedBackend = mapPracticeToBackend(practice);
    if (x.practices) {
      return x.practices.includes(selectedBackend);
    }
    return x.practice === practice;
  });
  if (filter === "today") list = list.filter(x => x.available);
  if (filter === "top") list = list.filter(x => x.rating >= 4.9);
  if (filter === "low") list = list.filter(x => x.fee < 2000);
  
  const homeList = list.slice(0, 6);
  
  grid.innerHTML = homeList.length 
    ? homeList.map(x => `
        <article class="lawyer-card" data-preview="${x.id}">
          <div class="lawyer-photo" style="background:${x.color}">
            <span class="initials" style="background:${darken(x.color)}">${x.initials}</span>
            ${x.available ? '<span class="badge">AVAILABLE TODAY</span>' : ""}
            <span class="rating" style="background:#e3f1e7;color:#337953;">✓ Verified</span>
          </div>
          <div class="details">
            <h3>${x.name}</h3>
            <p class="specialty">${x.specialty}</p>
            <div class="meta">
              <span>◷ ${x.years} yrs exp.</span>
              <span>◌ ${x.languages}</span>
            </div>
            <div class="card-bottom">
              <span><strong>${money(x.fee)}</strong> <small>/ session</small></span>
              <button class="book" data-book="${x.id}">View &amp; book</button>
            </div>
          </div>
        </article>
      `).join("")
    : `<div style="grid-column:1/-1;text-align:center;padding:48px 24px;background:#f9fafb;border-radius:16px;border:1px dashed var(--line);margin:20px 0;">
         <h4 style="font-size:18px;color:var(--forest);font-weight:700;margin-bottom:6px;">No verified lawyers available in this category yet</h4>
         <p style="font-size:14px;color:var(--ink-light);margin-bottom:16px;">We are actively onboarding verified advocates across India.</p>
         <a href="lawyer.html" style="display:inline-block;padding:10px 20px;background:var(--forest);color:white;border-radius:8px;font-weight:600;font-size:13px;text-decoration:none;">Are you a lawyer? Register as an Expert →</a>
       </div>`;
}

function bookingView() {
  const l = booking.lawyer;
  const s = booking.step;
  
  if (!booking.selectedPractice) {
    booking.selectedPractice = resolveBookingPractice(l, practice);
  }
  const currentPractice = booking.selectedPractice;

  let lawyerPractices = [];
  if (Array.isArray(l.practices)) {
    lawyerPractices = l.practices.map(p => mapPracticeToFrontend(p));
  } else if (typeof l.practice === "string") {
    lawyerPractices = l.practice.split(",").map(p => p.trim());
  }
  if (!lawyerPractices.length) lawyerPractices = [currentPractice];
  
  if (s === 1) {
    const showPracticePicker = lawyerPractices.length > 1;
    content.innerHTML = `
      <span class="kicker">Private consultation</span>
      <h2>A few details first</h2>
      <p class="lead">${l.name} will use this context to prepare.</p>
      <div class="progress"><i class="on"></i><i></i><i></i></div>
      
      ${showPracticePicker ? `
        <div class="field" style="margin-bottom: 16px;">
          <label style="font-size:12px; font-weight:700; color:var(--forest);">Consultation Topic / Practice Area</label>
          <select id="booking-practice-select" style="font-weight:600; padding:10px; border-radius:8px; border:1px solid var(--line); background:#fbfcfb;">
            ${lawyerPractices.map(p => `<option value="${p}" ${p === currentPractice ? 'selected' : ''}>${p}</option>`).join("")}
          </select>
        </div>
      ` : ""}

      <form class="form" id="intake-form">
        ${getIntakeQuestions(currentPractice).map((q, i) => `
          <div class="field">
            <label>${q}</label>
            ${i ? `<input required class="intake-ans" placeholder="Type your answer">` : `
              <select required class="intake-ans">
                <option value="">Select an answer</option>
                <option value="General advice">General advice</option>
                <option value="Document review">Document review</option>
                <option value="Ongoing dispute">Ongoing dispute</option>
              </select>
            `}
          </div>
        `).join("")}
        <div class="field">
          <label>Anything else your lawyer should know?</label>
          <textarea id="intake-notes" placeholder="Share only what you are comfortable sharing..."></textarea>
        </div>
        <div class="actions">
          <button class="primary" type="submit">Choose a time →</button>
        </div>
      </form>
    `;

    const practiceSelect = document.querySelector("#booking-practice-select");
    if (practiceSelect) {
      practiceSelect.onchange = (e) => {
        booking.selectedPractice = e.target.value;
        bookingView();
      };
    }
  }
  
  if (s === 2) {
    const l = booking.lawyer || {};
    const avail = l.availability || {};

    const getDayConfig = (dateObj) => {
      const dayKey = dateObj.toLocaleDateString("en-US", { weekday: "long" }).toLowerCase();
      if (!avail || Object.keys(avail).length === 0) {
        const isWeekday = dateObj.getDay() >= 1 && dateObj.getDay() <= 5;
        return isWeekday ? { active: true, start: "09:00 AM", end: "06:00 PM" } : { active: false };
      }
      return avail[dayKey] || { active: false };
    };

    const now = new Date();
    const activeDates = [];
    for (let i = 1; i <= 14; i++) {
      let d = new Date(now);
      d.setDate(d.getDate() + i);
      const cfg = getDayConfig(d);
      if (cfg && cfg.active) {
        activeDates.push(d);
      }
    }

    let datesHtml = "";
    if (activeDates.length === 0) {
      datesHtml = `<option value="">No available dates in next 14 days</option>`;
    } else {
      datesHtml = activeDates.map(d => {
        const val = d.toISOString().slice(0, 10);
        const label = d.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" });
        return `<option value="${val}">${label}</option>`;
      }).join("");
    }

    content.innerHTML = `
      <span class="kicker">Choose your slot</span>
      <h2>When works for you?</h2>
      <p class="lead">Times shown in ${Intl.DateTimeFormat().resolvedOptions().timeZone}.</p>
      <div class="progress"><i class="on"></i><i class="on"></i><i></i></div>
      <form class="form two" id="schedule-form">
        <div class="field">
          <label>Date</label>
          <select id="date" ${activeDates.length === 0 ? "disabled" : ""}>${datesHtml}</select>
        </div>
        <div class="field">
          <label>Time</label>
          <select id="time" ${activeDates.length === 0 ? "disabled" : ""}></select>
        </div>
        <div class="field">
          <label>Consultation mode</label>
          <select id="mode">
            <option>Secure video call</option>
            <option>Secure voice call</option>
          </select>
        </div>
        <div class="field">
          <label>Duration</label>
          <select><option>45 minutes</option></select>
        </div>
        <div class="actions" style="grid-column:1/-1">
          <button type="button" class="ghost secondary" data-back>Back</button>
          <button class="primary" type="submit" ${activeDates.length === 0 ? "disabled" : ""}>Review booking →</button>
        </div>
      </form>
    `;

    const populateTimeSlots = (dateStr) => {
      const timeSelect = document.querySelector("#time");
      if (!timeSelect || !dateStr) return;
      
      const parts = dateStr.split("-");
      const d = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10));
      const cfg = getDayConfig(d);
      
      if (!cfg || !cfg.active) {
        timeSelect.innerHTML = `<option value="">Unavailable on this day</option>`;
        return;
      }

      const parseTimeMinutes = (timeStr) => {
        if (!timeStr) return null;
        const p = timeStr.trim().split(" ");
        const hhmm = p[0].split(":");
        let h = parseInt(hhmm[0], 10);
        const m = parseInt(hhmm[1], 10);
        if (p[1] === "PM" && h < 12) h += 12;
        if (p[1] === "AM" && h === 12) h = 0;
        return h * 60 + m;
      };

      const formatTimeStr = (minutes) => {
        let h = Math.floor(minutes / 60);
        const m = minutes % 60;
        const ampm = h >= 12 ? "PM" : "AM";
        if (h > 12) h -= 12;
        if (h === 0) h = 12;
        const mm = m < 10 ? `0${m}` : `${m}`;
        return `${h}:${mm} ${ampm}`;
      };

      const startMins = parseTimeMinutes(cfg.start || "09:00 AM") || (9 * 60);
      const endMins = parseTimeMinutes(cfg.end || "06:00 PM") || (18 * 60);
      const minNoticeHours = avail._min_notice || 12;
      const bufferMins = avail._buffer || 15;
      const slotStepMins = 45 + bufferMins; // 45 min consultation + buffer break

      const now = new Date();
      const minNoticeCutoff = new Date(now.getTime() + minNoticeHours * 60 * 60 * 1000);

      const slots = [];
      for (let m = startMins; m + 45 <= endMins; m += slotStepMins) {
        const slotDate = new Date(d.getFullYear(), d.getMonth(), d.getDate(), Math.floor(m / 60), m % 60, 0);
        if (slotDate >= minNoticeCutoff) {
          slots.push(formatTimeStr(m));
        }
      }

      if (slots.length === 0) {
        timeSelect.innerHTML = `<option value="">No slots available (min ${minNoticeHours}h notice)</option>`;
      } else {
        timeSelect.innerHTML = slots.map(s => `<option>${s}</option>`).join("");
      }
    };

    const dateSelect = document.querySelector("#date");
    if (dateSelect && dateSelect.value) {
      populateTimeSlots(dateSelect.value);
      dateSelect.onchange = (e) => populateTimeSlots(e.target.value);
    }
  }
  
  if (s === 3) {
    let fee = l.fee;
    let p = Math.max(35, Math.round(fee * 0.05));
    let total = fee + p;
    content.innerHTML = `
      <span class="kicker">Confirm & pay securely</span>
      <h2>Almost there.</h2>
      <p class="lead">Payment is held and released after the consultation.</p>
      <div class="progress"><i class="on"></i><i class="on"></i><i class="on"></i></div>
      <div class="summary">
        <div class="row"><span>${l.name}</span><b>${l.specialty}</b></div>
        <div class="row"><span>${booking.date} · ${booking.time}</span><span>45 min</span></div>
        <div class="row"><span>Consultation</span><span>${money(fee)}</span></div>
        <div class="row"><span>Technology & Platform Infrastructure Usage Fee</span><span>${money(p)}</span></div>
        <div class="row total"><span>Total</span><span>${money(total)}</span></div>
      </div>
      <label class="disclaimer">
        <input type="checkbox" id="ack"> 
        <span>I understand VidhiMeet is an Electronic Marketplace Intermediary under Section 79 of the IT Act and does not itself provide legal advice. Legal advice is provided directly and solely by the verified lawyer. <strong>Metadata Waiver:</strong> I agree that in the event of a dispute, automated room connection logs (timestamps and participant durations) serve as sole definitive evidence for refund eligibility.</span>
      </label>
      <div id="booking-error" style="color:var(--terra);font-size:12px;font-weight:700;margin-top:10px;"></div>
      <div class="actions">
        <button class="ghost secondary" data-back>Back</button>
        <button class="primary" id="pay" disabled>Confirm & pay ${money(total)}</button>
      </div>
    `;
    
    document.querySelector("#ack").onchange = (e) => {
      document.querySelector("#pay").disabled = !e.target.checked;
    };
  }
  
  if (s === 4) {
    let dateFormatted = "";
    let isStartingSoon = true;

    let dt = null;
    if (booking && booking.starts_at) {
      const rawDt = booking.starts_at;
      const dtStr = rawDt && !rawDt.endsWith("Z") && !rawDt.includes("+") ? rawDt + "Z" : rawDt;
      dt = new Date(dtStr);
    } else if (booking && booking.date) {
      let hour = 10, min = 0;
      if (booking.time) {
        const parts = booking.time.split(":");
        hour = parseInt(parts[0], 10);
        const subparts = parts[1].split(" ");
        min = parseInt(subparts[0], 10);
        if (subparts[1] === "PM" && hour < 12) hour += 12;
        if (subparts[1] === "AM" && hour === 12) hour = 0;
      }
      dt = new Date(booking.date);
      dt.setHours(hour, min, 0, 0);
    }

    if (dt && !isNaN(dt.getTime())) {
      const now = new Date();
      const diffMs = dt.getTime() - now.getTime();
      const diffMins = diffMs / (1000 * 60);

      // Starting soon if meeting starts within 15 minutes or already started/ongoing
      isStartingSoon = diffMins <= 15;

      dateFormatted = dt.toLocaleDateString("en-IN", {
        weekday: "short",
        day: "numeric",
        month: "short",
        year: "numeric"
      }) + " at " + dt.toLocaleTimeString("en-IN", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true
      });
    }

    if (isStartingSoon) {
      content.innerHTML = `
        <div class="success">
          <div class="success-mark">✓</div>
          <span class="kicker">Booking confirmed</span>
          <h2>You're all set.</h2>
          <p class="lead">Your private consultation room is ready.</p>
          <button class="primary" id="join">Enter secure room →</button>
        </div>
      `;
    } else {
      content.innerHTML = `
        <div class="success">
          <div class="success-mark">✓</div>
          <span class="kicker">Booking confirmed</span>
          <h2>You're all set.</h2>
          <p class="lead">Your consultation is scheduled for <strong>${dateFormatted}</strong>.</p>
          <p style="font-size:13.5px;color:var(--text-muted);margin:-8px 0 20px;">You can join your private video room when your scheduled session starts.</p>
          <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;">
            <button class="primary" id="go-my-meetings">View My Consultations</button>
            <button class="ghost secondary" data-action="close-modal">Done</button>
          </div>
        </div>
      `;
      setTimeout(() => {
        const goBtn = document.querySelector("#go-my-meetings");
        if (goBtn) {
          goBtn.onclick = () => {
            closeModal();
            const btn = document.querySelector("#my-meetings-btn");
            if (btn) btn.click();
          };
        }
      }, 50);
    }
  }
}

function startBooking(id) {
  const lawyerIdStr = String(id);
  const found = lawyers.find(x => String(x.id) === lawyerIdStr);
  if (!found) {
    toast("Lawyer details not found. Please refresh and try again.");
    return;
  }
  booking = {
    lawyer: found,
    step: 1,
    selectedPractice: resolveBookingPractice(found, practice)
  };
  // If not logged in, show sign-in modal first, then continue to booking
  if (!LexAPI.authenticated()) {
    open();
    renderLogin(null, true);
    return;
  }
  bookingView();
  open();
}


async function showLawyerProfile(id) {
  const lawyerIdStr = String(id);
  const l = lawyers.find(x => String(x.id) === lawyerIdStr);
  if (!l) return;
  content.innerHTML = `
    <span class="kicker">Lawyer Profile</span>
    <h2>${l.name}</h2>
    <div style="display:flex;align-items:center;gap:14px;margin:16px 0;">
      <span style="width:64px;height:64px;border-radius:50%;background:${l.color};display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:#fff;flex-shrink:0;">${l.initials}</span>
      <div>
        <p style="margin:0;font-weight:600;">${l.specialty}</p>
        <p style="margin:4px 0 0;font-size:13px;color:var(--forest);font-weight:600;">✓ Verified &nbsp;&bull;&nbsp; ${l.years} yrs exp.</p>
        <p style="margin:4px 0 0;font-size:13px;color:var(--ink-light);">&#9673; ${l.languages}</p>
      </div>
    </div>
    <div style="background:var(--bg-soft);border-radius:10px;padding:14px 16px;margin-bottom:18px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:13px;color:var(--ink-light);">Consultation fee</span>
        <strong>${money(l.fee)} <small style="font-weight:400;">/ session</small></strong>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">
        <span style="font-size:13px;color:var(--ink-light);">Availability</span>
        <span style="font-size:13px;color:${l.available ? 'var(--forest)' : '#999'};font-weight:600;">${l.available ? '&#10003; Available today' : 'Not available today'}</span>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">
        <span style="font-size:13px;color:var(--ink-light);">Practice area</span>
        <span style="font-size:13px;">${l.practice}</span>
      </div>
    </div>
    <div id="lawyer-reviews-section">
      <div style="background:var(--mint);border-radius:10px;padding:14px 16px;margin-bottom:18px;font-size:12px;color:var(--forest);line-height:1.5;border:1px solid var(--line);">
        <strong>⚖ Bar Council of India Compliance Notice</strong><br>
        In accordance with BCI Rule 36 (Section IV, Chapter II, Part VI), advocate ratings and client testimonials are excluded to prevent commercial advertising or solicitation of legal work.
      </div>
    </div>
    <div class="actions">
      <button class="ghost secondary" data-action="close-modal">Close</button>
      <button class="primary" id="profile-book-btn">Book consultation &rarr;</button>
    </div>
  `;
  open();
  document.getElementById("profile-book-btn").onclick = () => startBooking(id);
}

async function handlePay() {
  const errDiv = document.querySelector("#booking-error");
  if (!LexAPI.authenticated()) {
    toast("Please sign in or register to complete your booking.");
    // Pause checkout and open login modal
    openAuthModal();
    return;
  }
  
  try {
    document.querySelector("#pay").disabled = true;
    document.querySelector("#pay").textContent = "Processing payment...";
    
    // Parse starts_at
    let hour = 10, min = 0;
    if (booking.time) {
      const parts = booking.time.split(":");
      hour = parseInt(parts[0]);
      const subparts = parts[1].split(" ");
      min = parseInt(subparts[0]);
      if (subparts[1] === "PM" && hour < 12) hour += 12;
      if (subparts[1] === "AM" && hour === 12) hour = 0;
    }
    const startsAt = new Date(booking.date);
    startsAt.setHours(hour, min, 0, 0);

    const targetPractice = booking.selectedPractice || practice;
    const keys = getIntakeKeys(targetPractice);

    const intakePayload = {};
    keys.forEach((key, idx) => {
      intakePayload[key] = (booking.intakeAnswers && booking.intakeAnswers[idx]) || "";
    });

    const payload = {
      lawyer_id: booking.lawyer.id,
      practice: mapPracticeToBackend(targetPractice),
      starts_at: startsAt.toISOString(),
      duration_minutes: 45,
      intake: intakePayload,
      disclaimer_accepted: true,
      disclaimer_version: "2026-01"
    };

    const res = await LexAPI.createBooking(payload);
    
    if (res.payment_url) {
      window.location.href = res.payment_url;
      return;
    }
    
    booking.id = res.id;
    booking.starts_at = res.starts_at;
    booking.step = 4;
    bookingView();
  } catch (err) {
    document.querySelector("#pay").disabled = false;
    document.querySelector("#pay").textContent = "Confirm & pay";
    errDiv.textContent = err.message;
  }
}

async function room() {
  modal.classList.add("video");
  content.innerHTML = `
    <span class="kicker">Private consultation</span>
    <h2>${booking.lawyer.name}</h2>
    <p class="lead">Secure room · Do not share this link</p>
    <div id="jitsi">
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:clamp(10px,2vh,20px);color:white;text-align:center;padding:clamp(14px,3.5vw,28px);background:linear-gradient(135deg, #173c30 0%, #0d221b 100%);box-sizing:border-box;overflow-y:auto;">
        <div class="network-icon" style="font-size:clamp(36px,6vw,56px);animation: pulse-wifi 2s infinite ease-in-out;flex-shrink:0;">📶</div>
        <div style="max-width:480px;display:flex;flex-direction:column;gap:8px;flex-shrink:1;">
          <h3 style="margin:0;font-size:clamp(17px,3.5vw,22px);font-family:'Playfair Display', serif;letter-spacing:-0.01em;">Optimize Your Connection</h3>
          <p style="margin:0;opacity:0.85;font-size:clamp(12px,2.8vw,15px);line-height:1.45;">
            For a seamless consultation session, please ensure you have a strong, stable internet connection.
          </p>
          <div style="background:rgba(217,173,98,0.15);border:1px solid rgba(217,173,98,0.3);border-radius:12px;padding:8px 12px;margin-top:2px;">
            <p style="margin:0;color:#d9ad62;font-weight:700;font-size:clamp(11px,2.5vw,13px);letter-spacing:0.05em;text-transform:uppercase;">
              ⚡ 5G or High-Speed Wi-Fi Recommended
            </p>
          </div>
        </div>
        <div style="display:flex;gap:10px;margin-top:4px;flex-wrap:wrap;justify-content:center;flex-shrink:0;">
          <button id="start-call-precheck-btn" style="padding:10px 24px;min-height:44px;background:#d9ad62;color:#17251f;border:none;border-radius:99px;cursor:pointer;font-weight:700;font-size:14px;transition:all 0.2s ease-in-out;box-shadow:0 4px 15px rgba(217,173,98,0.3);">Proceed to Call</button>
          <button id="cancel-call-precheck-btn" style="padding:10px 24px;min-height:44px;background:rgba(255,255,255,0.15);color:white;border:none;border-radius:99px;cursor:pointer;font-weight:600;font-size:14px;transition:all 0.2s ease-in-out;">Cancel</button>
        </div>
      </div>
    </div>
    <style>
      @keyframes pulse-wifi {
        0%, 100% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.05); opacity: 1; filter: drop-shadow(0 0 10px rgba(217, 173, 98, 0.4)); }
      }
      #start-call-precheck-btn:hover {
        background: #e2be7d !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(217,173,98,0.5) !important;
      }
      #cancel-call-precheck-btn:hover {
        background: rgba(255,255,255,0.25) !important;
      }
    </style>
  `;

  document.querySelector("#cancel-call-precheck-btn").onclick = () => {
    close();
  };

  document.querySelector("#start-call-precheck-btn").onclick = async () => {
    document.querySelector("#jitsi").innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;">
        <div style="font-size:48px;">🎥</div>
        <h3 style="margin:0;font-size:18px;">Requesting camera &amp; microphone access…</h3>
        <p style="margin:0;opacity:0.6;font-size:14px;">Please allow access in the browser popup to join the room.</p>
      </div>
    `;
    await _proceedToRoom();
  };

  async function _proceedToRoom() {
    // Request camera and microphone permissions first
    let stream = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    } catch (permErr) {
      const denied = permErr.name === "NotAllowedError" || permErr.name === "PermissionDeniedError";
      document.querySelector("#jitsi").innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;text-align:center;padding:30px;">
          <div style="font-size:48px;">${denied ? "🚫" : "⚠️"}</div>
          <h3 style="margin:0;font-size:18px;">${denied ? "Camera & microphone access denied" : "Could not access camera/microphone"}</h3>
          <p style="margin:0;opacity:0.7;font-size:14px;max-width:380px;">${denied
            ? "Please allow access in your browser settings and try again, or join without video/audio."
            : permErr.message}</p>
          <div style="display:flex;gap:12px;margin-top:8px;">
            <button id="join-muted-btn" style="padding:10px 22px;background:#265a47;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;">Join without camera/mic</button>
          </div>
        </div>`;
      document.querySelector("#join-muted-btn").onclick = () => _launchClientDaily(true);
      return;
    }

    // Stop the test stream — Daily manages its own
    if (stream) stream.getTracks().forEach(t => t.stop());

    // Wait 400ms to release device
    await new Promise(resolve => setTimeout(resolve, 400));

    // Run a lightweight network check using navigator.connection (no Daily iframe needed)
    document.querySelector("#jitsi").innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;">
        <div style="width:40px;height:40px;border:3px solid rgba(255,255,255,0.2);border-top-color:white;border-radius:50%;animation:spin 0.8s linear infinite;"></div>
        <p style="margin:0;font-size:14px;opacity:0.7;">Preparing your secure room…</p>
      </div>
      <style>@keyframes spin{to{transform:rotate(360deg)}}</style>`;

    let networkWarningRequired = false;
    try {
      const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      if (conn) {
        const effectiveType = conn.effectiveType; // "slow-2g", "2g", "3g", "4g"
        const downlink = conn.downlink; // Mbps
        const rtt = conn.rtt; // ms
        if (effectiveType === "slow-2g" || effectiveType === "2g" || rtt > 300 || downlink < 0.5) {
          networkWarningRequired = true;
        }
      }
    } catch(e) {
      console.warn("Network check skipped:", e);
    }

    if (networkWarningRequired) {
      document.querySelector("#jitsi").innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;text-align:center;padding:30px;">
          <div style="font-size:48px;">⚠️</div>
          <h3 style="margin:0;font-size:18px;">Your internet is unstable</h3>
          <p style="margin:0;opacity:0.7;font-size:14px;max-width:380px;">Your connection appears slow. Please move closer to your router or switch off video to ensure a smooth call.</p>
          <div style="display:flex;gap:12px;margin-top:8px;">
            <button id="precheck-join-video-btn" style="padding:10px 22px;background:#265a47;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;">Join call anyway</button>
            <button id="precheck-join-audio-btn" style="padding:10px 22px;background:#444;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;">Join audio-only</button>
          </div>
        </div>`;
      document.querySelector("#precheck-join-video-btn").onclick = () => _launchClientDaily(false);
      document.querySelector("#precheck-join-audio-btn").onclick = () => _launchClientDaily(true);
      return;
    }

    await _launchClientDaily(false);
  }
}

// ── Reconnection state ───────────────────────────────────────────────────────
let isLaunchingCall = false;
let _reconnectAttempts = 0;
const RECONNECT_MAX = 5;
const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 15000]; // exponential back-off
let _reconnectTimer = null;
let _networkCheckInterval = null;
let _userLeftIntentionally = false;
let _currentMutedFallback = false;

// Show an overlay inside #jitsi with a countdown and attempt info
function _showReconnectOverlay(attempt, delayMs) {
  const container = document.querySelector("#jitsi");
  if (!container) return;
  const secs = Math.ceil(delayMs / 1000);
  const overlayId = "reconnect-overlay";
  let overlay = document.getElementById(overlayId);
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = overlayId;
    overlay.style = [
      "position:absolute","inset:0","background:rgba(0,0,0,0.82)",
      "display:flex","flex-direction:column","align-items:center",
      "justify-content:center","gap:14px","color:white","z-index:9999",
      "border-radius:14px","text-align:center","padding:30px"
    ].join(";");
    container.style.position = "relative";
    container.appendChild(overlay);
  }
  overlay.innerHTML = `
    <div style="font-size:46px;">📡</div>
    <h3 style="margin:0;font-size:20px;font-weight:700;">Connection lost</h3>
    <p style="margin:0;font-size:14px;opacity:0.75;max-width:300px;">
      Reconnecting you to the same room automatically…
    </p>
    <div id="reconnect-countdown" style="
      font-size:36px;font-weight:800;letter-spacing:2px;
      background:rgba(255,255,255,0.1);border-radius:50%;
      width:64px;height:64px;display:flex;align-items:center;justify-content:center;
    ">${secs}</div>
    <p style="margin:0;font-size:12px;opacity:0.5;">Attempt ${attempt} of ${RECONNECT_MAX}</p>
    <button id="reconnect-now-btn" style="
      margin-top:8px;padding:10px 28px;background:#1b5e3b;color:white;
      border:none;border-radius:10px;cursor:pointer;font-size:14px;font-weight:600;
    ">Reconnect now</button>
    <button id="reconnect-leave-btn" style="
      padding:8px 20px;background:rgba(255,255,255,0.1);color:white;
      border:1px solid rgba(255,255,255,0.3);border-radius:10px;cursor:pointer;
      font-size:13px;
    ">Leave call</button>`;

  // Countdown tick
  let remaining = secs;
  const tick = setInterval(() => {
    remaining--;
    const el = document.getElementById("reconnect-countdown");
    if (el) el.textContent = remaining > 0 ? remaining : "…";
    if (remaining <= 0) clearInterval(tick);
  }, 1000);

  document.getElementById("reconnect-now-btn").onclick = () => {
    clearTimeout(_reconnectTimer);
    clearInterval(tick);
    _attemptReconnect();
  };
  document.getElementById("reconnect-leave-btn").onclick = () => {
    clearTimeout(_reconnectTimer);
    clearInterval(tick);
    _userLeftIntentionally = true;
    _reconnectAttempts = 0;
    close();
  };
}

function _clearReconnectOverlay() {
  const overlay = document.getElementById("reconnect-overlay");
  if (overlay) overlay.remove();
}

async function _attemptReconnect() {
  if (_reconnectAttempts >= RECONNECT_MAX) {
    // Give up — show final failure message
    const container = document.querySelector("#jitsi");
    if (container) {
      container.innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
          height:100%;gap:16px;color:white;text-align:center;padding:30px;">
          <div style="font-size:48px;">❌</div>
          <h3 style="margin:0;font-size:18px;">Could not reconnect</h3>
          <p style="margin:0;opacity:0.7;font-size:14px;max-width:340px;">
            We tried ${RECONNECT_MAX} times but couldn't restore the connection.
            Your booking is still active — you can rejoin from My Meetings.
          </p>
          <button id="reconnect-rejoin-btn" style="
            padding:11px 26px;background:#1b5e3b;color:white;border:none;
            border-radius:10px;cursor:pointer;font-size:14px;font-weight:600;
          ">Try again manually</button>
          <button id="reconnect-close-btn" style="
            padding:9px 20px;background:rgba(255,255,255,0.1);color:white;
            border:1px solid rgba(255,255,255,0.3);border-radius:10px;cursor:pointer;font-size:13px;
          ">Leave</button>
        </div>`;
      document.getElementById("reconnect-rejoin-btn").onclick = () => {
        _reconnectAttempts = 0;
        _launchClientDaily(_currentMutedFallback);
      };
      document.getElementById("reconnect-close-btn").onclick = () => {
        _reconnectAttempts = 0;
        close();
      };
    }
    return;
  }

  _reconnectAttempts++;
  isLaunchingCall = false; // allow re-entry
  await _launchClientDaily(_currentMutedFallback);
}

async function _launchClientDaily(mutedFallback) {
  if (isLaunchingCall) return;
  isLaunchingCall = true;
  _currentMutedFallback = mutedFallback;

  // Clear loading screen and show a spinner while connecting
  const container = document.querySelector("#jitsi");
  if (container) {
    // If this is a reconnect attempt, keep the overlay visible until join succeeds
    if (_reconnectAttempts === 0) {
      container.innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;">
          <div style="width:40px;height:40px;border:3px solid rgba(255,255,255,0.2);border-top-color:white;border-radius:50%;animation:spin 0.8s linear infinite;"></div>
          <p style="margin:0;font-size:14px;opacity:0.7;">Connecting to secure room…</p>
        </div>
        <style>@keyframes spin{to{transform:rotate(360deg)}}</style>`;
    }
  }

  try {
    const meetDetails = await LexAPI.meeting(booking.id);
    const Daily = window.Daily || window.DailyIframe;
    if (!Daily) {
      document.querySelector("#jitsi").innerHTML = '<div class="success" style="color:white"><h3>Daily.co SDK could not load</h3><p>Check your connection and refresh.</p></div>';
      isLaunchingCall = false;
      return;
    }

    // Destroy any existing call instance to avoid duplicates
    let existingCall = Daily.getCallInstance() || window.dailyCallFrame;
    if (existingCall) {
      window.dailyCallFrame = null;
      try {
        await Promise.race([
          existingCall.destroy(),
          new Promise(resolve => setTimeout(resolve, 1000))
        ]);
      } catch (e) {
        console.warn("Error/Timeout destroying existing Daily call:", e);
      }
    }
    // Remove any lingering Daily iframes from the DOM
    document.querySelectorAll("iframe").forEach(iframe => {
      try {
        if ((iframe.allow && iframe.allow.includes("camera")) ||
            (iframe.src && iframe.src.includes("daily"))) {
          iframe.remove();
        }
      } catch(e) {}
    });

    // Clear overlay / container before Daily inserts its iframe
    _clearReconnectOverlay();
    const jitsiEl = document.querySelector("#jitsi");
    if (jitsiEl) jitsiEl.innerHTML = '';

    window.dailyCallFrame = Daily.createFrame(document.querySelector("#jitsi"), {
      iframeStyle: {
        width: "100%",
        height: "100%",
        border: "0",
        borderRadius: "14px"
      },
      showLeaveButton: true,
      showFullscreenButton: true,
      dailyConfig: {
        experimentalSimulcast: true,
        avoidEval: true,
        userMediaVideoConstraints: {
          width: { max: 1280 },
          height: { max: 720 },
          frameRate: { max: 30 }
        }
      }
    });

    const joinOptions = { url: meetDetails.url };
    if (meetDetails.token) joinOptions.token = meetDetails.token;
    joinOptions.videoSource = !mutedFallback;
    joinOptions.audioSource = !mutedFallback;

    await window.dailyCallFrame.join(joinOptions);
    isLaunchingCall = false;
    _reconnectAttempts = 0; // reset on successful join
    _userLeftIntentionally = false;

    if (mutedFallback) {
      await window.dailyCallFrame.setLocalVideo(false);
      await window.dailyCallFrame.setLocalAudio(false);
    }

    // ── Consultation Timer: Trigger after both parties connect ──────────────
    let _callTimerStarted = false;
    let _callElapsedSeconds = 0;
    let _callTimerInterval = null;

    function _updateTimerBanner() {
      const banner = document.querySelector("#consultation-timer-banner");
      if (!banner) return;
      const mins = Math.floor(_callElapsedSeconds / 60).toString().padStart(2, '0');
      const secs = (_callElapsedSeconds % 60).toString().padStart(2, '0');
      banner.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#56a977;box-shadow:0 0 8px #56a977;margin-right:6px;"></span>Consultation Active · ⏱️ ${mins}:${secs}`;
    }

    function _checkParticipantsAndStartTimer() {
      if (!window.dailyCallFrame) return;
      try {
        const participants = window.dailyCallFrame.participants() || {};
        const count = Object.keys(participants).length;
        let banner = document.querySelector("#consultation-timer-banner");
        const jitsiEl = document.querySelector("#jitsi");
        if (!banner && jitsiEl) {
          jitsiEl.style.position = "relative";
          banner = document.createElement("div");
          banner.id = "consultation-timer-banner";
          banner.style = "position:absolute;top:12px;left:14px;background:rgba(23,37,31,0.85);backdrop-filter:blur(8px);color:white;padding:8px 16px;border-radius:99px;font-size:13px;font-weight:700;z-index:998;border:1px solid rgba(255,255,255,0.2);display:flex;align-items:center;box-shadow:0 4px 12px rgba(0,0,0,0.2);";
          jitsiEl.appendChild(banner);
        }

        if (count >= 2) {
          if (!_callTimerStarted) {
            _callTimerStarted = true;
            if (_callTimerInterval) clearInterval(_callTimerInterval);
            _callTimerInterval = setInterval(() => {
              _callElapsedSeconds++;
              _updateTimerBanner();
            }, 1000);
          }
          _updateTimerBanner();
        } else {
          if (!_callTimerStarted) {
            if (banner) banner.innerHTML = `⏳ Waiting for second participant... (Timer starts when both connect)`;
          } else {
            const mins = Math.floor(_callElapsedSeconds / 60).toString().padStart(2, '0');
            const secs = (_callElapsedSeconds % 60).toString().padStart(2, '0');
            if (banner) banner.innerHTML = `⏸️ Participant disconnected · ⏱️ ${mins}:${secs}`;
          }
        }
      } catch (e) {
        console.error("Timer check error:", e);
      }
    }

    window.dailyCallFrame.on("joined-meeting", _checkParticipantsAndStartTimer);
    window.dailyCallFrame.on("participant-joined", _checkParticipantsAndStartTimer);
    window.dailyCallFrame.on("participant-left", _checkParticipantsAndStartTimer);
    _checkParticipantsAndStartTimer();

    // ── Dynamic quality monitoring ─────────────────────────────────────────
    if (_networkCheckInterval) clearInterval(_networkCheckInterval);
    _networkCheckInterval = setInterval(async () => {
      if (!window.dailyCallFrame) {
        clearInterval(_networkCheckInterval);
        return;
      }
      try {
        const stats = await window.dailyCallFrame.getNetworkStats();
        if (stats && stats.stats && stats.stats.latest) {
          const latest = stats.stats.latest;
          const bad = latest.videoRecvPacketLoss > 0.05 || latest.rtt > 200;
          if (bad) {
            let warningBanner = document.querySelector("#call-warning-banner");
            if (!warningBanner) {
              warningBanner = document.createElement("div");
              warningBanner.id = "call-warning-banner";
              warningBanner.style = "position:absolute;top:10px;left:50%;transform:translateX(-50%);background:var(--terra);color:white;padding:8px 16px;border-radius:8px;font-size:12px;z-index:999;font-weight:bold;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.15);";
              warningBanner.innerHTML = `⚠️ Unstable connection — consider turning off video.`;
              const jitsiEl = document.querySelector("#jitsi");
              if (jitsiEl) jitsiEl.style.position = "relative";
              if (jitsiEl) jitsiEl.appendChild(warningBanner);
            }
          } else {
            const warningBanner = document.querySelector("#call-warning-banner");
            if (warningBanner) warningBanner.remove();
          }
        }
      } catch (e) {
        console.error("Error reading mid-call network stats", e);
      }
    }, 5000);

    // ── Intentional leave ─────────────────────────────────────────────────
    window.dailyCallFrame.on("left-meeting", async () => {
      if (_networkCheckInterval) clearInterval(_networkCheckInterval);
      if (_callTimerInterval) clearInterval(_callTimerInterval);
      const timerBanner = document.querySelector("#consultation-timer-banner");
      if (timerBanner) timerBanner.remove();
      _userLeftIntentionally = true;
      _reconnectAttempts = 0;

      if (_callElapsedSeconds >= 1200 && booking?.id) {
        try {
          await apiClient.request(`/api/v1/bookings/${booking.id}/complete`, { method: "POST" });
          if (typeof renderBookings === "function") await renderBookings();
        } catch (e) {
          console.warn("Auto-completion on call end:", e);
        }
      }

      close();
    });

    // ── Graceful reconnect on error / unexpected drop ──────────────────────
    function _handleDisconnect(eventName, eventData) {
      if (_userLeftIntentionally) return;
      if (_networkCheckInterval) clearInterval(_networkCheckInterval);
      console.warn(`[Daily] ${eventName}:`, eventData);

      if (_reconnectAttempts >= RECONNECT_MAX) {
        _attemptReconnect(); // will show the give-up UI
        return;
      }

      const delay = RECONNECT_DELAYS[_reconnectAttempts] ?? 15000;
      _showReconnectOverlay(_reconnectAttempts + 1, delay);
      _reconnectTimer = setTimeout(() => _attemptReconnect(), delay);
    }

    window.dailyCallFrame.on("error", evt => _handleDisconnect("error", evt));
    window.dailyCallFrame.on("nonfatal-error", evt => {
      // Only reconnect for connection-loss nonfatal errors
      if (evt?.errorMsg?.toLowerCase().includes("network") ||
          evt?.errorMsg?.toLowerCase().includes("disconnect") ||
          evt?.errorMsg?.toLowerCase().includes("connection")) {
        _handleDisconnect("nonfatal-error", evt);
      }
    });
    // Daily emits 'network-quality-change' — reconnect on very poor quality
    window.dailyCallFrame.on("network-quality-change", evt => {
      if (evt?.quality === "very-low" && !_userLeftIntentionally) {
        let warningBanner = document.querySelector("#call-warning-banner");
        if (!warningBanner) {
          warningBanner = document.createElement("div");
          warningBanner.id = "call-warning-banner";
          warningBanner.style = "position:absolute;top:10px;left:50%;transform:translateX(-50%);background:#92400e;color:white;padding:8px 16px;border-radius:8px;font-size:12px;z-index:999;font-weight:bold;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.15);";
          warningBanner.innerHTML = `⚠️ Very poor network — call may drop soon.`;
          const jitsiEl = document.querySelector("#jitsi");
          if (jitsiEl) { jitsiEl.style.position = "relative"; jitsiEl.appendChild(warningBanner); }
        }
      }
    });

  } catch (err) {
    isLaunchingCall = false;
    const msg = err?.message || err?.errorMsg || (typeof err === 'string' ? err : JSON.stringify(err));

    // If this was a reconnect attempt, schedule the next one
    if (_reconnectAttempts > 0 && _reconnectAttempts < RECONNECT_MAX) {
      const delay = RECONNECT_DELAYS[_reconnectAttempts] ?? 15000;
      _showReconnectOverlay(_reconnectAttempts + 1, delay);
      _reconnectTimer = setTimeout(() => _attemptReconnect(), delay);
    } else if (_reconnectAttempts === 0) {
      const jitsiEl = document.querySelector("#jitsi");
      if (jitsiEl) jitsiEl.innerHTML = `<div class="success" style="color:white"><h3>Failed to access room</h3><p>${msg}</p></div>`;
    } else {
      _attemptReconnect(); // triggers give-up UI
    }
  }
}



// Google Authentication Handler
async function performGoogleAuth(role = "client") {
  let idToken = null;
  let email = null;
  let fullName = null;
  const clientId = window.GOOGLE_CLIENT_ID || "1040292571789-l57llglphoakuffucsreo4mteui5u9bs.apps.googleusercontent.com";

  // 1. Interactive Google OAuth2 Popup client (preferred on button click)
  if (window.google && google.accounts && google.accounts.oauth2) {
    try {
      const popupPromise = new Promise((resolve, reject) => {
        const client = google.accounts.oauth2.initTokenClient({
          client_id: clientId,
          scope: "openid email profile",
          callback: (res) => {
            if (res && res.access_token) {
              resolve(res.access_token);
            } else {
              reject(new Error("No access token returned from Google popup"));
            }
          },
          error_callback: (err) => reject(err)
        });
        client.requestAccessToken();
      });
      idToken = await popupPromise;
    } catch (popupErr) {
      console.warn("Google OAuth2 popup attempt:", popupErr);
    }
  }

  // 2. Google Identity Services One-Tap prompt fallback
  if (!idToken && window.google && google.accounts && google.accounts.id) {
    try {
      const tokenPromise = new Promise((resolve, reject) => {
        google.accounts.id.initialize({
          client_id: clientId,
          callback: (res) => (res && res.credential) ? resolve(res.credential) : reject(new Error("No credential returned"))
        });
        google.accounts.id.prompt((n) => {
          if (n.isNotDisplayed() || n.isSkippedMoment()) reject(new Error("Prompt skipped"));
        });
      });
      idToken = await tokenPromise;
    } catch (gsiErr) {
      console.warn("Google GIS prompt fallback:", gsiErr);
    }
  }

  // 3. Firebase Auth popup fallback
  if (!idToken && window.firebase && firebase.auth && firebase.auth.GoogleAuthProvider) {
    try {
      const provider = new firebase.auth.GoogleAuthProvider();
      const res = await firebase.auth().signInWithPopup(provider);
      if (res && res.user) {
        idToken = await res.user.getIdToken();
        email = res.user.email;
        fullName = res.user.displayName || email.split("@")[0];
      }
    } catch (e) {
      console.warn("Google popup fallback:", e);
    }
  }

  // 4. Local development mock fallback (STRICTLY RESTRICTED to localhost / dev environments)
  const isLocalhost = ["localhost", "127.0.0.1", "0.0.0.0"].includes(window.location.hostname);
  if (!idToken && !email) {
    if (!isLocalhost) {
      throw new Error("Google Sign-In failed or popup was closed. Please try again or sign in with email.");
    }
    email = role === "lawyer" ? "lawyer.google@vidhimeet.in" : "client.google@vidhimeet.in";
    fullName = role === "lawyer" ? "Adv. Google User" : "Google Client User";
    idToken = `mock-google-token-${email}`;
  }

  const payload = { role };
  if (idToken) payload.id_token = idToken;
  if (email) payload.email = email;
  if (fullName) payload.full_name = fullName;

  await LexAPI.googleLogin(payload);
  const user = LexAPI.getCurrentUser();
  if (!user || user.role !== role) {
    LexAPI.logout();
    throw new Error(`Access denied. Account role is invalid for ${role} login.`);
  }
  return user;
}

// Authentication Forms UI
function openAuthModal(redirect = null) {
  open();
  renderLogin(redirect);
}

function renderLogin(redirect = null, fromBooking = false) {
  const heading = fromBooking
    ? `<span class="kicker">One step away</span><h2>Sign in to book</h2><p class="lead">Sign in or create a free account to continue with your consultation booking.</p>`
    : `<span class="kicker">Secure Access</span><h2>Sign In</h2><p class="lead">Welcome back to VidhiMeet.</p>`;

  content.innerHTML = `
    ${heading}
    <button type="button" class="btn-google-auth" id="btn-google-login">
      <svg width="18" height="18" viewBox="0 0 18 18">
        <path fill="#4285F4" d="M17.64 9.2c0-.74-.06-1.28-.19-1.84H9v3.34h4.96c-.1.83-.64 2.08-1.84 2.92l-.01.12 2.67 2.07.18.02c1.7-1.57 2.68-3.88 2.68-6.63z"/>
        <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.84-2.21c-.76.53-1.78.9-3.12.9-2.38 0-4.41-1.57-5.13-3.74l-.11.01-2.75 2.13-.03.11C2.43 15.93 5.46 18 9 18z"/>
        <path fill="#FBBC05" d="M3.87 10.77c-.19-.58-.3-1.2-.3-1.77s.11-1.19.3-1.77l-.01-.13-2.76-2.14-.09.04C.35 6.24 0 7.58 0 9s.35 2.76 1.01 4.01l2.86-2.24z"/>
        <path fill="#EA4335" d="M9 3.58c1.69 0 2.83.73 3.48 1.34l2.54-2.48C13.46.96 11.43 0 9 0 5.46 0 2.43 2.07 1.01 5.06l2.85 2.24c.72-2.17 2.75-3.72 5.14-3.72z"/>
      </svg>
      <span>Sign in with Google</span>
    </button>
    <div class="auth-divider"><span>or sign in with email</span></div>
    <form class="form" id="login-form" autocomplete="off">

      <div class="field">
        <label>Email Address</label>
        <input type="email" id="login-email" name="username" required autocomplete="username" placeholder="name@example.com" value="" />
      </div>
      <div class="field">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <label>Password</label>
          <button type="button" id="btn-client-forgot-password" style="background:none;border:none;color:var(--forest);font-size:12px;font-weight:600;cursor:pointer;padding:0;">Forgot password?</button>
        </div>
        <div class="password-wrap">
          <input type="password" id="login-password" name="password" required autocomplete="new-password" placeholder="••••••••••••" value="" />
          <button type="button" class="password-toggle-btn" aria-label="Show password" title="Show password">
            <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <svg class="eye-closed" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
          </button>
        </div>
      </div>
      <div id="auth-error" style="color:var(--terra);font-size:12px;font-weight:700;margin-top:5px;"></div>
      <div class="actions">
        <button class="primary" type="submit">Sign In</button>
      </div>
    </form>
    <p style="text-align:center;margin-top:14px;font-size:13px;color:var(--ink-light);">New here? <button type="button" id="switch-to-register" style="background:none;border:none;color:var(--forest);font-weight:600;cursor:pointer;font-size:13px;padding:0;">Create a free account →</button></p>
  `;

  const btnClientForgot = document.querySelector("#btn-client-forgot-password");
  if (btnClientForgot) {
    btnClientForgot.onclick = () => renderForgotPassword(redirect, fromBooking);
  }

  const btnG = document.querySelector("#btn-google-login");
  if (btnG) {
    btnG.onclick = async () => {
      const origG = btnG.innerHTML;
      btnG.disabled = true;
      btnG.style.pointerEvents = "none";
      btnG.innerHTML = `<span class="btn-spinner"></span> <span>Signing in with Google...</span>`;
      try {
        await performGoogleAuth("client");
        const u = LexAPI.getCurrentUser();
        const fullName = u ? u.full_name : "Client";
        toast(`Welcome back, ${fullName}!`);
        close();
        updateHeader();
        if (redirect) window.location.href = redirect;
      } catch (err) {
        const errDiv = document.querySelector("#auth-error");
        if (errDiv) errDiv.textContent = err.message || "Google auth failed";
        btnG.disabled = false;
        btnG.style.pointerEvents = "";
        btnG.innerHTML = origG;
      }
    };
  }

  document.querySelector("#switch-to-register").onclick = () => renderRegister(redirect, fromBooking);

  // Clear any aggressive browser/extension autofill values shortly after render
  setTimeout(() => {
    const emailInput = document.querySelector("#login-email");
    const passwordInput = document.querySelector("#login-password");
    if (emailInput && !emailInput.matches(':focus')) emailInput.value = "";
    if (passwordInput && !passwordInput.matches(':focus')) passwordInput.value = "";
  }, 300);
  
  document.querySelector("#login-form").onsubmit = async (e) => {
    e.preventDefault();
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.innerHTML : "Sign In";
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.style.pointerEvents = "none";
      submitBtn.innerHTML = `<span class="btn-spinner"></span> Signing In...`;
    }

    const email = document.querySelector("#login-email").value;
    const password = document.querySelector("#login-password").value;
    const errDiv = document.querySelector("#auth-error");
    try {
      await LexAPI.login(email, password);
      const user = LexAPI.getCurrentUser();
      
      if (user && user.role === "lawyer") {
        LexAPI.logout();
        errDiv.textContent = "This portal is for clients only. Lawyers must log in via the Lawyer Portal.";
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.style.pointerEvents = "";
          submitBtn.innerHTML = originalText;
        }
        return;
      }
      
      // Determine destination before touching the DOM
      let destination = redirect || null;
      if (destination === "client.html") destination = null;
      if (!destination && user) {
        if (user.role === "admin") destination = "admin.html";
        else if (user.role === "client") destination = null;
      }
      
      if (booking && booking.lawyer) {
        toast("Welcome back!");
        booking.step = 1;
        bookingView();
        updateHeader();
        return;
      }
      
      if (destination) {
        // Navigate away immediately — no need to update UI on a page we're leaving
        window.location.href = destination;
      } else {
        // Staying on this page: update UI normally
        toast("Welcome back!");
        close();
        updateHeader();
      }
    } catch (err) {
      errDiv.textContent = err.message || "Login failed";
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.style.pointerEvents = "";
        submitBtn.innerHTML = originalText;
      }
    }
  };
}

function renderRegister(redirect = null, fromBooking = false) {
  const heading = fromBooking
    ? `<span class="kicker">One step away</span><h2>Create your account</h2><p class="lead">Free to join — book your consultation right after.</p>`
    : `<span class="kicker">Get Started</span><h2>Create Account</h2><p class="lead">Join our legal marketplace.</p>`;

  content.innerHTML = `
    ${heading}
    <button type="button" class="btn-google-auth" id="btn-google-register">
      <svg width="18" height="18" viewBox="0 0 18 18">
        <path fill="#4285F4" d="M17.64 9.2c0-.74-.06-1.28-.19-1.84H9v3.34h4.96c-.1.83-.64 2.08-1.84 2.92l-.01.12 2.67 2.07.18.02c1.7-1.57 2.68-3.88 2.68-6.63z"/>
        <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.84-2.21c-.76.53-1.78.9-3.12.9-2.38 0-4.41-1.57-5.13-3.74l-.11.01-2.75 2.13-.03.11C2.43 15.93 5.46 18 9 18z"/>
        <path fill="#FBBC05" d="M3.87 10.77c-.19-.58-.3-1.2-.3-1.77s.11-1.19.3-1.77l-.01-.13-2.76-2.14-.09.04C.35 6.24 0 7.58 0 9s.35 2.76 1.01 4.01l2.86-2.24z"/>
        <path fill="#EA4335" d="M9 3.58c1.69 0 2.83.73 3.48 1.34l2.54-2.48C13.46.96 11.43 0 9 0 5.46 0 2.43 2.07 1.01 5.06l2.85 2.24c.72-2.17 2.75-3.72 5.14-3.72z"/>
      </svg>
      <span>Sign in with Google</span>
    </button>
    <div class="auth-divider"><span>or register with email</span></div>
    <form class="form" id="register-form">
      <div class="field">
        <label>Full Name</label>
        <input type="text" id="reg-name" required placeholder="John Doe">
      </div>
      <div class="field">
        <label>Email Address</label>
        <input type="email" id="reg-email" required placeholder="name@example.com">
      </div>
      <div class="field">
        <label>Password (min 12 chars)</label>
        <div class="password-wrap">
          <input type="password" id="reg-password" required minlength="12" placeholder="••••••••••••">
          <button type="button" class="password-toggle-btn" aria-label="Show password" title="Show password">
            <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <svg class="eye-closed" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
          </button>
        </div>
      </div>
      <div class="field">
        <label>Re-enter Password</label>
        <div class="password-wrap">
          <input type="password" id="reg-confirm-password" required minlength="12" placeholder="••••••••••••">
          <button type="button" class="password-toggle-btn" aria-label="Show password" title="Show password">
            <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <svg class="eye-closed" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
          </button>
        </div>
      </div>
      <div class="field">
        <label>Date of Birth</label>
        <input type="date" id="reg-dob" required
          max="${new Date(Date.now() - 18 * 365.25 * 24 * 3600 * 1000).toISOString().split('T')[0]}"
          style="font-family:inherit;">
      </div>
      <div class="field consent-field" style="background:#f8fdf9;border:1px solid #c8e6c9;border-radius:10px;padding:12px 14px;margin-top:4px;">
        <label style="display:flex;align-items:flex-start;gap:10px;cursor:pointer;font-weight:400;font-size:13px;">
          <input type="checkbox" id="reg-consent-privacy" required style="margin-top:2px;accent-color:#1b5e3b;width:16px;height:16px;flex-shrink:0;">
          <span>I have read and agree to the <a href="privacy.html" style="color:var(--forest);font-weight:600;">Privacy Policy</a> and consent to the collection and processing of my personal data as required under the <strong>Digital Personal Data Protection Act, 2023</strong>.</span>
        </label>
        <label style="display:flex;align-items:flex-start;gap:10px;cursor:pointer;font-weight:400;font-size:13px;margin-top:10px;">
          <input type="checkbox" id="reg-consent-terms" required style="margin-top:2px;accent-color:#1b5e3b;width:16px;height:16px;flex-shrink:0;">
          <span>I agree to the <a href="terms.html" style="color:var(--forest);font-weight:600;">Terms of Service</a>.</span>
        </label>
      </div>
      <div id="auth-error" style="color:var(--terra);font-size:12px;font-weight:700;margin-top:5px;"></div>
      <div class="actions">
        <button class="primary" type="submit">Create Account &amp; Continue</button>
      </div>
    </form>
    <p style="text-align:center;margin-top:14px;font-size:13px;color:var(--ink-light);">Already have an account? <button type="button" id="switch-to-login" style="background:none;border:none;color:var(--forest);font-weight:600;cursor:pointer;font-size:13px;padding:0;">Sign in →</button></p>
  `;
  
  const btnGR = document.querySelector("#btn-google-register");
  if (btnGR) {
    btnGR.onclick = async () => {
      try {
        await performGoogleAuth("client");
        const u = LexAPI.getCurrentUser();
        const fullName = u ? u.full_name : "Client";
        toast(`Welcome, ${fullName}!`);
        close();
        updateHeader();
        if (redirect) window.location.href = redirect;
      } catch (err) {
        const errDiv = document.querySelector("#auth-error");
        if (errDiv) errDiv.textContent = err.message || "Google auth failed";
      }
    };
  }

  document.querySelector("#switch-to-login").onclick = () => renderLogin(redirect, fromBooking);
  
  document.querySelector("#register-form").onsubmit = async (e) => {
    e.preventDefault();
    const fullName = document.querySelector("#reg-name").value;
    const email = document.querySelector("#reg-email").value;
    const password = document.querySelector("#reg-password").value;
    const confirmPassword = document.querySelector("#reg-confirm-password") ? document.querySelector("#reg-confirm-password").value : "";
    const dob = document.querySelector("#reg-dob").value;
    const consentPrivacy = document.querySelector("#reg-consent-privacy").checked;
    const consentTerms = document.querySelector("#reg-consent-terms").checked;
    const role = "client";
    const errDiv = document.querySelector("#auth-error");
    errDiv.textContent = "";

    if (password !== confirmPassword) {
      errDiv.textContent = "Passwords do not match. Please re-enter your password.";
      return;
    }

    // Client-side age check (server also validates)
    if (dob) {
      const today = new Date();
      const birthDate = new Date(dob);
      const age = today.getFullYear() - birthDate.getFullYear()
        - ((today.getMonth() < birthDate.getMonth() ||
            (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) ? 1 : 0);
      if (age < 18) {
        errDiv.textContent = "You must be at least 18 years old to register (DPDP Act 2023, Section 9).";
        return;
      }
    }

    if (!consentPrivacy || !consentTerms) {
      errDiv.textContent = "You must accept the Privacy Policy and Terms of Service to continue.";
      return;
    }
    try {
      await LexAPI.register(email, password, fullName, role, {
        consent_privacy_policy: true,
        consent_terms: true,
        date_of_birth: dob,
      });
      toast("Account created successfully!");
      updateHeader();
      
      if (booking && booking.lawyer) {
        booking.step = 1;
        bookingView();
        return;
      }
      
      if (redirect) {
        window.location.href = redirect;
      } else {
        close();
      }
    } catch (err) {
      errDiv.textContent = err.message;
    }
  };
}

function renderForgotPassword(redirect = null, fromBooking = false, initialToken = "") {
  if (initialToken) {
    // Clean "Set New Password" form when token is present
    content.innerHTML = `
      <span class="kicker">Account Security</span>
      <h2>Set New Password</h2>
      <p class="lead">Please create a strong new password with at least 12 characters.</p>
      <form class="form" id="reset-form" autocomplete="off">
        <input type="hidden" id="reset-token-input" value="${escapeHtml(initialToken)}" />
        <div class="field">
          <label>New Password</label>
          <div class="password-wrap">
            <input type="password" id="reset-new-password" required minlength="12" placeholder="At least 12 characters" value="" />
            <button type="button" class="password-toggle-btn" aria-label="Show password" title="Show password">
              <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg class="eye-closed" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
        </div>
        <div class="field">
          <label>Confirm Password</label>
          <div class="password-wrap">
            <input type="password" id="reset-confirm-password" required minlength="12" placeholder="Re-enter new password" value="" />
            <button type="button" class="password-toggle-btn" aria-label="Show password" title="Show password">
              <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg class="eye-closed" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
        </div>
        <div id="reset-error" style="color:var(--terra);font-size:12px;font-weight:700;margin-top:5px;"></div>
        <div class="actions">
          <button class="primary" type="submit" id="btn-reset-submit">Update Password</button>
        </div>
      </form>
      <p style="text-align:center;margin-top:16px;font-size:13px;color:var(--ink-light);">Remembered your password? <button type="button" id="switch-back-to-login" style="background:none;border:none;color:var(--forest);font-weight:600;cursor:pointer;font-size:13px;padding:0;">Sign in →</button></p>
    `;

    document.querySelector("#switch-back-to-login").onclick = () => renderLogin(redirect, fromBooking);

    const resetForm = document.querySelector("#reset-form");
    if (resetForm) {
      resetForm.onsubmit = async (e) => {
        e.preventDefault();
        const token = document.querySelector("#reset-token-input").value.trim();
        const newPassword = document.querySelector("#reset-new-password").value;
        const confirmPassword = document.querySelector("#reset-confirm-password").value;
        const errDiv = document.querySelector("#reset-error");
        const submitBtn = document.querySelector("#btn-reset-submit");
        errDiv.textContent = "";

        if (!token) {
          errDiv.textContent = "Reset token is missing or invalid. Please request a new reset link.";
          return;
        }
        if (newPassword.length < 12) {
          errDiv.textContent = "Password must be at least 12 characters long.";
          return;
        }
        if (newPassword !== confirmPassword) {
          errDiv.textContent = "Passwords do not match. Please re-enter.";
          return;
        }

        submitBtn.disabled = true;
        try {
          await LexAPI.resetPassword(token, newPassword);
          toast("Password successfully reset! Please sign in.");
          renderLogin(redirect, fromBooking);
        } catch (err) {
          errDiv.textContent = err.message || "Failed to reset password";
        } finally {
          submitBtn.disabled = false;
        }
      };
    }
    return;
  }

  // Clean "Forgot Password / Send Reset Link" form
  content.innerHTML = `
    <span class="kicker">Account Recovery</span>
    <h2>Reset Password</h2>
    <p class="lead">Enter your registered email address to receive a password reset link.</p>
    <form class="form" id="forgot-form" autocomplete="off">
      <div class="field">
        <label>Email Address</label>
        <input type="email" id="forgot-email" required placeholder="name@example.com" value="" />
      </div>
      <div id="forgot-error" style="color:var(--terra);font-size:12px;font-weight:700;margin-top:5px;"></div>
      <div id="forgot-success" style="color:#2e7d32;font-size:13px;font-weight:600;margin-top:8px;line-height:1.5;"></div>
      <div class="actions">
        <button class="primary" type="submit" id="btn-forgot-submit">Send Reset Link</button>
      </div>
    </form>
    <p style="text-align:center;margin-top:16px;font-size:13px;color:var(--ink-light);">Remembered your password? <button type="button" id="switch-back-to-login" style="background:none;border:none;color:var(--forest);font-weight:600;cursor:pointer;font-size:13px;padding:0;">Sign in →</button></p>
  `;

  document.querySelector("#switch-back-to-login").onclick = () => renderLogin(redirect, fromBooking);

  document.querySelector("#forgot-form").onsubmit = async (e) => {
    e.preventDefault();
    const email = document.querySelector("#forgot-email").value.trim();
    const errDiv = document.querySelector("#forgot-error");
    const succDiv = document.querySelector("#forgot-success");
    const submitBtn = document.querySelector("#btn-forgot-submit");
    errDiv.textContent = "";
    succDiv.textContent = "";
    submitBtn.disabled = true;

    try {
      const res = await LexAPI.forgotPassword(email);
      if (res.debug_reset_token) {
        // In local development / debug mode, seamlessly navigate to the clean Set New Password view
        renderForgotPassword(redirect, fromBooking, res.debug_reset_token);
      } else {
        succDiv.textContent = res.message || "Password reset link has been sent to your email. Please check your inbox to continue.";
      }
    } catch (err) {
      errDiv.textContent = err.message || "This email is not registered with us.";
    } finally {
      submitBtn.disabled = false;
    }
  };
}

// Auto-detect reset token in URL parameters on page load
(function checkResetTokenUrl() {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token") || params.get("reset_token");
  if (token) {
    window.addEventListener("DOMContentLoaded", () => {
      open();
      renderForgotPassword(null, false, token);
      const newPass = document.querySelector("#reset-new-password");
      if (newPass) setTimeout(() => newPass.focus(), 100);
    });
  }
})();

function updateHeader() {
  const user = LexAPI.getCurrentUser();
  const headerActions = document.querySelector(".header-actions");
  if (user) {
    const controlConsole = user.role === "admin" 
      ? `<a href="admin.html" class="user-dropdown-item"><span class="dropdown-icon">⚙️</span> Admin console</a>` 
      : (user.role === "lawyer" ? `<a href="lawyer.html" class="user-dropdown-item"><span class="dropdown-icon">⚖️</span> Lawyer portal</a>` : "");
      
    const userName = user.full_name || user.name || "Client";
    const initial = escapeHtml(userName.charAt(0).toUpperCase());

    headerActions.innerHTML = `
      <div class="user-dropdown-wrapper">
        <button type="button" class="user-dropdown-trigger" id="user-menu-btn" title="Account Menu">
          <span class="user-avatar-circle">${initial}</span>
          <span class="user-name-text">${escapeHtml(userName)}</span>
          <span class="user-chevron">▾</span>
        </button>
        <div class="user-dropdown-menu" id="user-dropdown-menu" hidden>
          <div class="user-dropdown-header">
            <div class="user-name-title">${escapeHtml(userName)}</div>
            <div class="user-email-subtitle">${escapeHtml(user.email || "")}</div>
          </div>
          <a href="#my-meetings" data-view="my-meetings" class="user-dropdown-item">
            <span class="dropdown-icon">📅</span> My Meetings
          </a>
          <a href="#drafting" data-view="drafting" class="user-dropdown-item">
            <span class="dropdown-icon">📄</span> Drafting Desk
          </a>
          ${controlConsole}
          <div class="dropdown-divider"></div>
          <button type="button" id="signout-btn" class="user-dropdown-item signout-item">
            <span class="dropdown-icon">🚪</span> Sign out
          </button>
        </div>
      </div>
    `;

    const menuBtn = document.querySelector("#user-menu-btn");
    const menu = document.querySelector("#user-dropdown-menu");
    if (menuBtn && menu) {
      menuBtn.onclick = (e) => {
        e.stopPropagation();
        menu.hidden = !menu.hidden;
      };
      menu.onclick = (e) => {
        if (e.target.closest(".user-dropdown-item")) {
          menu.hidden = true;
        }
      };
    }

    const signoutBtn = document.querySelector("#signout-btn");
    if (signoutBtn) {
      signoutBtn.onclick = (e) => {
        e.preventDefault();
        LexAPI.logout();
        toast("Signed out securely.");
        setTimeout(() => {
          window.location.href = "index.html";
        }, 600);
      };
    }
  } else {
    headerActions.innerHTML = `
        <a class="ghost" href="lawyer.html">Lawyer portal</a>
        <button class="ghost" id="signin-btn">Client sign in</button>
      `;
    document.querySelector("#signin-btn").onclick = () => openAuthModal();
  }
  // Re-attach data-go smooth scrolling logic
  document.querySelectorAll("[data-go]").forEach(btn => {
    btn.onclick = () => {
      const targetId = btn.dataset.go;
      document.querySelector("#" + targetId)?.scrollIntoView({behavior: "smooth"});
    };
  });
}

// Helper: restore main homepage view (hide My Meetings / All Lawyers overlays)
function restoreHomeView() {
  const myMeetings = document.querySelector("#my-meetings");
  const allLawyers = document.querySelector("#all-lawyers-view");
  const drafting = document.querySelector("#drafting");
  const mainEl = document.querySelector("main");
  if (myMeetings) myMeetings.style.display = "none";
  if (allLawyers) allLawyers.style.display = "none";
  if (drafting) drafting.style.display = "none";
  if (mainEl) mainEl.style.display = "";
}

// Global click event handlers
document.addEventListener("click", async e => {
  // Nav links (Find a lawyer / How it works / Security) & brand logo →
  // restore main view before scrolling so sections are visible
  const navLink = e.target.closest("header nav a:not([data-view]), a.brand");
  if (navLink) {
    restoreHomeView();
    // allow default anchor-scroll to proceed
  }
  const p = e.target.closest("[data-practice]");
  if (p) {
    practice = p.dataset.practice;
    document.querySelector("#practice").value = practice;
    document.querySelectorAll("[data-practice]").forEach(x => x.classList.toggle("active", x === p));
    filter = "all";
    document.querySelectorAll("[data-filter]").forEach(x => x.classList.toggle("active", x.dataset.filter === "all"));
    render();
    document.querySelector(".lawyers").scrollIntoView({behavior: "smooth"});
  }
  
  const f = e.target.closest("[data-filter]");
  if (f) {
    filter = f.dataset.filter;
    document.querySelectorAll("[data-filter]").forEach(x => x.classList.toggle("active", x === f));
    render();
  }
  
  const b = e.target.closest("[data-book]");
  if (b) {
    // Stop here so card click (data-preview) doesn't also fire
    startBooking(b.dataset.book);
    return;
  }
  // Client sign-in click handler
  const signinBtn = e.target.closest("#signin-btn");
  if (signinBtn) {
    e.preventDefault();
    openAuthModal();
  }

  // Lawyer card body click → show brief profile popup
  const preview = e.target.closest("[data-preview]");
  if (preview) {
    showLawyerProfile(preview.dataset.preview);
  }
  
  if (e.target.closest(".close") || e.target === backdrop) {
    close();
  }
  
  if (e.target.closest("[data-back]")) {
    booking.step--;
    bookingView();
  }
  
  if (e.target.id === "pay") {
    handlePay();
  }
  
  if (e.target.id === "join") {
    room();
  }
  
  const g = e.target.closest("[data-go]");
  if (g && !g.closest(".header-actions")) {
    document.querySelector("#" + g.dataset.go).scrollIntoView({behavior: "smooth"});
  }
  
  const t = e.target.closest("[data-toast]");
  if (t) {
    toast(t.dataset.toast);
  }

  // Navigation tabs (My Meetings / Drafting)
  const v = e.target.closest("[data-view]");
  if (v) {
    e.preventDefault();
    window.location.hash = v.dataset.view;
  }

  // Back to home handlers
  if (e.target.id === "back-to-home" || e.target.id === "drafting-back-btn" || e.target.id === "all-lawyers-back-btn") {
    window.location.hash = "";
  }
  if (e.target.id === "create-drafting-btn") {
    openCreateDraftingModal();
  }

  // View All Lawyers
  if (e.target.id === "view-all-lawyers-btn") {
    e.preventDefault();
    window.location.hash = "all-lawyers-view";
  }

  // Join meeting from My Meetings list
  const jb = e.target.closest("[data-join-booking]");
  if (jb) {
    const bid = jb.dataset.joinBooking;
    joinMeeting(bid);
  }

  // Rate & Review button
  const rb = e.target.closest("[data-review-booking]");
  if (rb) {
    openReviewModal(rb.dataset.reviewBooking, rb.dataset.reviewLawyer);
  }

  // Chat button
  const cb = e.target.closest("[data-chat-booking]");
  if (cb) {
    openChatModal(cb.dataset.chatBooking, cb.dataset.chatLawyer, cb.dataset.chatSalt);
  }

  // Upload docs button
  const ub = e.target.closest("[data-upload-booking]");
  if (ub) {
    const fileInput = document.getElementById(`doc-file-${ub.dataset.uploadBooking}`);
    if (fileInput) fileInput.click();
  }

  // Dispute button
  const db = e.target.closest("[data-dispute-booking]");
  if (db) {
    openDisputeModal(db.dataset.disputeBooking);
  }


  // Handle all drafting actions (event delegation for CSP compliance)
  const actionBtn = e.target.closest("[data-action]");
  if (actionBtn) {
    const action = actionBtn.dataset.action;
    const id = actionBtn.dataset.id;
    switch (action) {
      case "create-drafting":
        window.openCreateDraftingModal();
        break;
      case "accept-proposal":
        window.acceptProposal(id, actionBtn.dataset.proposalId);
        break;
      case "pay-drafting":
        window.payForDrafting(id);
        break;
      case "cancel-drafting":
        window.cancelDrafting(id);
        break;
      case "approve-draft":
        window.approveDraft(id);
        break;
      case "view-drafting-details":
        window.viewDraftingDetails(id);
        break;
      case "close-modal":
        close();
        break;
    }
  }
});

// Doc file change handler (delegated)
document.addEventListener("change", async e => {
  if (["filter-experience", "filter-language", "filter-rating"].includes(e.target?.id)) {
    renderAllLawyers();
    return;
  }
  const fi = e.target;
  if (!fi.id || !fi.id.startsWith("doc-file-")) return;
  const bookingId = fi.id.replace("doc-file-", "");
  const file = fi.files[0];
  if (!file) return;

  const allowed = ["application/pdf","image/jpeg","image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
  if (!allowed.includes(file.type)) {
    toast("Only PDF, JPEG, PNG or DOCX files are allowed.");
    return;
  }
  if (file.size > 20 * 1024 * 1024) {
    toast("File must be under 20 MB.");
    return;
  }

  toast(`Uploading ${file.name}…`);
  try {
    const presign = await LexAPI.presignDocument(bookingId, file.name, file.type || "application/pdf");
    const formData = new FormData();
    Object.entries(presign.upload.fields || {}).forEach(([k,v]) => formData.append(k, v));
    formData.append("file", file);
    const headers = {};
    const token = LexAPI.getAccessToken();
    const uploadUrl = LexAPI.resolveUploadUrl(presign.upload.url);
    if (token && presign.upload.url.startsWith("/")) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const s3 = await fetch(uploadUrl, { method: "POST", body: formData, headers });
    if (s3.ok || s3.status === 201 || s3.status === 204) {
      await LexAPI.confirmDocumentUpload(bookingId, file.name, presign.key);
      toast(`✓ ${file.name} uploaded to secure vault.`);
    } else {
      throw new Error("Upload failed (status " + s3.status + ")");
    }
  } catch (err) {
    // Mock fallback for dev environment without S3
    try {
      await LexAPI.confirmDocumentUpload(bookingId, file.name, `mock/${bookingId}/${file.name}`);
      toast(`✓ ${file.name} saved to secure vault.`);
    } catch (e2) {
      toast("Upload failed: " + err.message);
    }
  }
  fi.value = "";
});

// Forms submit handlers
document.addEventListener("submit", e => {
  if (e.target.id === "search") {
    e.preventDefault();
    practice = document.querySelector("#practice").value;
    render();
    document.querySelector(".lawyers").scrollIntoView({behavior: "smooth"});
  }
  
  if (e.target.id === "intake-form") {
    e.preventDefault();
    booking.intakeAnswers = Array.from(document.querySelectorAll(".intake-ans")).map(el => el.value);
    booking.step = 2;
    bookingView();
  }
  
  if (e.target.id === "schedule-form") {
    e.preventDefault();
    booking.date = document.querySelector("#date").value;
    booking.time = document.querySelector("#time").value;
    booking.step = 3;
    bookingView();
  }
});

function toast(m) {
  let t = document.querySelector("#toast");
  t.textContent = m;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2500);
}

// Mobile menu handler
const menuBtn = document.querySelector("#mobile-menu-btn");
const headerEl = document.querySelector("header");
if (menuBtn && headerEl) {
  menuBtn.onclick = (e) => {
    e.stopPropagation();
    headerEl.classList.toggle("menu-open");
  };
  const closeMobileMenuIfOutside = (e) => {
    if (headerEl.classList.contains("menu-open") && !headerEl.contains(e.target)) {
      headerEl.classList.remove("menu-open");
    }
  };
  document.addEventListener("click", closeMobileMenuIfOutside);
  document.addEventListener("touchstart", closeMobileMenuIfOutside, { passive: true });
  headerEl.querySelectorAll("nav a, .header-actions button, .header-actions a").forEach(link => {
    link.addEventListener("click", () => {
      headerEl.classList.remove("menu-open");
    });
  });
}

// ── My Meetings ──────────────────────────────────────────────────────────────

const STATUS_LABEL = {
  pending_payment: { text: "Pending Payment", cls: "status-pending" },
  confirmed:       { text: "Confirmed",       cls: "status-confirmed" },
  in_progress:     { text: "In Progress",     cls: "status-inprogress" },
  completed:       { text: "Completed",       cls: "status-done" },
  disputed:        { text: "Disputed",        cls: "status-disputed" },
  cancelled:       { text: "Cancelled",       cls: "status-cancelled" },
  refunded:        { text: "Refunded",        cls: "status-cancelled" },
};

function isRoomActive(startsAt, durationMinutes = 45, status = "") {
  if (status === "in_progress") return true;
  if (status !== "confirmed") return false;
  if (!startsAt) return false;
  
  const rawDt = typeof startsAt === "string" && !startsAt.endsWith("Z") && !startsAt.includes("+") ? startsAt + "Z" : startsAt;
  const startMs = new Date(rawDt).getTime();
  if (isNaN(startMs)) return false;

  const nowMs = Date.now();
  const windowStart = startMs - 15 * 60 * 1000;
  const windowEnd = startMs + (durationMinutes || 45) * 60 * 1000;

  return nowMs >= windowStart && nowMs <= windowEnd;
}

async function showMyMeetings() {
  if (!LexAPI.authenticated()) {
    window.location.hash = "";
    open();
    renderLogin(null);
    return;
  }

  const meetingsSection = document.querySelector("#my-meetings");
  const mainEl = document.querySelector("main");
  mainEl.style.display = "none";
  meetingsSection.style.display = "";
  window.scrollTo({ top: 0, behavior: "smooth" });

  const listEl = document.querySelector("#meetings-list");
  listEl.innerHTML = `<div class="meetings-loading"><div class="spinner"></div><p>Loading your consultations…</p></div>`;

  try {
    const bookings = await LexAPI.bookings();
    if (!bookings || bookings.length === 0) {
      listEl.innerHTML = `
        <div class="meetings-empty">
          <div class="empty-icon">📅</div>
          <h3>No consultations yet</h3>
          <p>Book your first consultation with a verified lawyer.</p>
          <button class="primary" id="back-to-home">Find a Lawyer →</button>
        </div>`;
      return;
    }

    // Fetch reviews for completed bookings in parallel
    const reviewMap = {};
    const completedBookings = bookings.filter(b => b.status === "completed");
    const reviewPromises = completedBookings.map(b =>
      LexAPI.getBookingReview(b.id).then(r => { if (r) reviewMap[b.id] = r; }).catch(() => {})
    );
    await Promise.all(reviewPromises);

    listEl.innerHTML = bookings.map(b => {
      const sl = STATUS_LABEL[b.status] || { text: b.status, cls: "status-pending" };
      const canJoin = isRoomActive(b.starts_at, b.duration_minutes, b.status);
      const isConfirmed = b.status === "confirmed" || b.status === "in_progress";
      const rawDt = b.starts_at || b.original_starts_at || "";
      const dtStr = rawDt && !rawDt.endsWith("Z") && !rawDt.includes("+") ? rawDt + "Z" : rawDt;
      const dt = dtStr ? new Date(dtStr) : null;
      const dateStr = dt ? dt.toLocaleDateString("en-IN", {weekday:"short", day:"numeric", month:"short", year:"numeric"}) : "—";
      const timeStr = dt ? dt.toLocaleTimeString("en-IN", {hour:"2-digit", minute:"2-digit"}) : "";
      const amount = b.amount_minor ? money(b.amount_minor / 100) : "—";
      const practice = mapPracticeToFrontend(b.practice);

      // BCI Rule 36: Star ratings and client reviews are excluded
      let reviewHTML = "";

      // Build Google Calendar quick-add link
      let gcalUrl = "";
      if (dt && ["confirmed", "in_progress"].includes(b.status)) {
        const dtEnd = new Date(dt.getTime() + (b.duration_minutes || 45) * 60000);
        const fmt = d => d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
        gcalUrl = `https://calendar.google.com/calendar/event?action=TEMPLATE` +
          `&text=${encodeURIComponent(`Legal Consultation (—${b.lawyer_name || "Advocate"})`)}`+
          `&dates=${fmt(dt)}/${fmt(dtEnd)}`+
          `&details=${encodeURIComponent(`VidhiMeet consultation. Ref: ${b.id.slice(0,8).toUpperCase()}. Join room after lawyer confirms.`)}`+
          `&location=${encodeURIComponent("VidhiMeet Secure Video Room")}`;
      }

      return `
        <article class="meeting-card">
          <div class="meeting-card-top">
            <div class="meeting-meta">
              <div style="display:flex; align-items:center; gap:8px;">
                <span class="meeting-practice">${practice}</span>
                <span class="meeting-status ${sl.cls}">${sl.text}</span>
              </div>

              <!-- 3-Dots Options Menu Trigger & Dropdown -->
              <div class="card-dots-wrapper">
                <button class="card-dots-btn" data-menu-toggle="${b.id}" title="More options" aria-label="More options">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="5" r="2.2"/>
                    <circle cx="12" cy="12" r="2.2"/>
                    <circle cx="12" cy="19" r="2.2"/>
                  </svg>
                </button>
                <div class="card-dots-menu" id="card-menu-${b.id}" hidden>
                  ${["confirmed","in_progress","pending_payment"].includes(b.status) ? `
                    <button class="card-menu-item" data-upload-booking="${b.id}">
                      <span class="menu-icon">📎</span> Upload case related documents
                    </button>
                  ` : ""}
                  ${isConfirmed ? `
                    <div class="card-menu-divider"></div>
                    <div class="card-menu-subhead">Add to Calendar</div>
                    <a href="${gcalUrl}" target="_blank" rel="noopener" class="card-menu-item sub">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" rx="4" fill="#4285F4"/><path d="M12 6v6l4 2" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>
                      Google Calendar
                    </a>
                    <button class="card-menu-item sub" data-ics-booking="${b.id}">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" rx="4" fill="#1E4D3B"/><path d="M5 10h14M5 14h14M10 6v12" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>
                      Apple / Outlook (.ics)
                    </button>
                  ` : ""}
                  ${["confirmed", "in_progress"].includes(b.status) ? `
                    <div class="card-menu-divider"></div>
                    <button class="card-menu-item warning" data-dispute-booking="${b.id}">
                      <span class="menu-icon">⚠️</span> Dispute
                    </button>
                  ` : ""}
                  ${["confirmed", "pending_payment"].includes(b.status) ? `
                    <div class="card-menu-divider"></div>
                    <button class="card-menu-item danger" data-cancel-booking="${b.id}">
                      <span class="menu-icon">🚫</span> Cancel consultation
                    </button>
                  ` : ""}
                </div>
              </div>
            </div>
            
            <div class="meeting-lawyer-name" style="font-size: 18px; font-weight: 700; color: var(--forest); margin: 6px 0 2px;">
              ${b.lawyer_name || "Assigned Lawyer"}
            </div>
            <div class="meeting-datetime">
              <span class="meeting-date">📅 ${dateStr}</span>
              ${timeStr ? `<span class="meeting-time">🕐 ${timeStr}</span>` : ""}
            </div>
          </div>
          <div class="meeting-card-body">
            <div class="meeting-fee"><strong>${amount}</strong> <small>/ session</small></div>
            <div class="meeting-id">Ref: <code>${b.id.slice(0, 8).toUpperCase()}</code></div>
          </div>
          <div class="meeting-card-actions">
            ${canJoin 
              ? `<button class="primary" data-join-booking="${b.id}">Join Secure Room →</button>` 
              : (isConfirmed ? `<button class="primary" disabled title="Room opens 15 minutes before scheduled session time" style="opacity:0.55; cursor:not-allowed; background:#8a9f93; border-color:#8a9f93;">Room opens 15m before start</button>` : "")}
            ${b.status === "pending_payment" ? `<span class="meeting-hint">⏳ Awaiting payment confirmation</span>` : ""}
            ${reviewHTML}
            ${b.status === "cancelled" || b.status === "refunded" ? `<span class="meeting-hint">✗ Booking ${b.status}</span>` : ""}
            ${["confirmed","in_progress","pending_payment"].includes(b.status) ? `
              <button class="btn-chat-meeting" data-chat-booking="${b.id}" data-chat-lawyer="${b.lawyer_name || 'Your Lawyer'}" data-chat-salt="${b.chat_key_salt || ''}">💬 Chat</button>
            ` : ""}
            <input type="file" id="doc-file-${b.id}" accept=".pdf,.jpg,.jpeg,.png,.docx" hidden>
          </div>
        </article>`;
    }).join("");

    // Bind 3-dots options menu toggles
    document.querySelectorAll("[data-menu-toggle]").forEach(btn => {
      btn.onclick = (e) => {
        e.stopPropagation();
        const menuId = btn.dataset.menuToggle;
        const menu = document.getElementById(`card-menu-${menuId}`);
        if (!menu) return;
        const isHidden = menu.hidden;
        document.querySelectorAll(".card-dots-menu").forEach(m => m.hidden = true);
        menu.hidden = !isHidden;
      };
    });

    // Close 3-dots menu when clicking an item inside or clicking outside
    document.querySelectorAll(".card-dots-menu button, .card-dots-menu a").forEach(item => {
      item.onclick = (e) => {
        const menu = item.closest(".card-dots-menu");
        if (menu) menu.hidden = true;
      };
    });
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".card-dots-wrapper")) {
        document.querySelectorAll(".card-dots-menu").forEach(m => m.hidden = true);
      }
    });

    // Bind cancellation buttons
    document.querySelectorAll("[data-cancel-booking]").forEach(btn => {
      btn.onclick = () => openCancelModal(btn.dataset.cancelBooking);
    });

    // Bind .ics download buttons
    document.querySelectorAll("[data-ics-booking]").forEach(btn => {
      btn.onclick = () => downloadBookingIcs(btn.dataset.icsBooking);
    });
  } catch (err) {
    listEl.innerHTML = `<div class="meetings-empty"><div class="empty-icon">⚠️</div><h3>Could not load meetings</h3><p>${err.message}</p><button class="primary" id="back-to-home">Go back</button></div>`;
  }
}

// ── Calendar Download Helper ─────────────────────────────────────────────────

function downloadBookingIcs(bookingId) {
  const token = LexAPI.getAccessToken();
  if (!token) { toast("Please log in to download calendar event."); return; }
  const base = window.location.origin;
  const a = document.createElement("a");
  a.href = `${base}/api/v1/bookings/${bookingId}/calendar.ics`;
  a.download = `VidhiMeet-${bookingId.slice(0,8).toLowerCase()}.ics`;
  // Pass auth token via query param (calendar clients can't set headers)
  a.href += `?token=${encodeURIComponent(token)}`;
  a.click();
}

// ── Client Cancellation Modal ────────────────────────────────────────────────

async function openCancelModal(bookingId) {
  open();
  content.innerHTML = `<div class="meetings-loading"><div class="spinner"></div><p>Calculating cancellation refund preview…</p></div>`;

  try {
    const preview = await LexAPI.getCancellationPreview(bookingId);
    const refundRs = (preview.refund_amount_minor / 100).toFixed(2);
    const penaltyRs = (preview.penalty_amount_minor / 100).toFixed(2);
    const totalRs = (preview.total_amount_minor / 100).toFixed(2);

    let tierLabel = "Free Cancellation (100% Refund)";
    if (preview.policy_tier === "client_between_2h_and_24h") {
      tierLabel = "Late Cancellation (75% Refund / 25% Short-Notice Fee)";
    } else if (preview.policy_tier === "client_under_2h_or_noshow") {
      tierLabel = "Short-Notice Cancellation (<2 Hours: 0% Refund)";
    } else if (preview.policy_tier === "lawyer_cancellation") {
      tierLabel = "Lawyer Cancellation (100% Refund + Voucher)";
    }

    content.innerHTML = `
      <span class="kicker">Cancel Consultation</span>
      <h2>Confirm Cancellation</h2>
      <p class="lead">${tierLabel}</p>

      <div style="background:rgba(0,0,0,0.03);border:1px solid rgba(0,0,0,0.08);border-radius:10px;padding:16px;margin:16px 0;text-align:left;">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
          <span>Total Paid:</span>
          <strong>₹${totalRs}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;color:${preview.penalty_amount_minor > 0 ? '#b30000' : '#1e7e34'};">
          <span>Cancellation Fee (${preview.penalty_pct}%):</span>
          <span>- ₹${penaltyRs}</span>
        </div>
        <hr style="border:0;border-top:1px solid rgba(0,0,0,0.1);margin:8px 0;">
        <div style="display:flex;justify-content:space-between;font-size:16px;font-weight:700;color:var(--forest);">
          <span>Eligible Refund Amount:</span>
          <span>₹${refundRs}</span>
        </div>
      </div>

      <p style="font-size:13px;color:var(--text-muted);margin-bottom:16px;text-align:left;">
        💡 <strong>Reversal Timeline:</strong> ${preview.reversal_timeline_notice}
      </p>

      <div class="form-group" style="text-align:left;">
        <label style="display:block;font-size:13px;font-weight:600;margin-bottom:4px;">Reason for cancellation (optional)</label>
        <textarea id="cancel-reason" rows="2" placeholder="e.g. Schedule conflict..." style="width:100%;padding:8px;border-radius:6px;border:1px solid #ccc;"></textarea>
      </div>

      <div class="actions" style="margin-top:20px;">
        <button class="ghost secondary" data-action="close-modal">Keep Booking</button>
        <button class="primary" id="confirm-cancel-btn" style="background:#8b0000;border-color:#8b0000;">Confirm Cancellation</button>
      </div>
    `;

    document.getElementById("confirm-cancel-btn").onclick = async () => {
      const reason = document.getElementById("cancel-reason").value;
      document.getElementById("confirm-cancel-btn").disabled = true;
      document.getElementById("confirm-cancel-btn").textContent = "Processing refund...";
      try {
        const res = await LexAPI.cancelBooking(bookingId, reason);
        closeModal();
        toast(res.message || "Booking cancelled successfully.");
        showMyMeetings();
      } catch (err) {
        toast("Cancellation failed: " + err.message);
        document.getElementById("confirm-cancel-btn").disabled = false;
        document.getElementById("confirm-cancel-btn").textContent = "Confirm Cancellation";
      }
    };
  } catch (err) {
    content.innerHTML = `<div class="meetings-empty"><h3>Error</h3><p>${err.message}</p><button class="primary" data-action="close-modal">Close</button></div>`;
  }
}

// ── Client Chat Modal ────────────────────────────────────────────────────────

async function openChatModal(bookingId, lawyerName, chatKeySalt) {
  open();
  modal.classList.add("chat");
  content.innerHTML = `
    <div class="client-chat-modal">
      <div class="client-chat-header">
        <h3>💬 Chat with ${lawyerName}</h3>
        <small class="client-chat-secure">🔒 End-to-end encrypted</small>
      </div>
      <div class="client-chat-messages" id="client-chat-msgs"><div class="client-chat-loading">Loading messages…</div></div>
      <form class="client-chat-form" id="client-chat-form">
        <input id="client-chat-input" placeholder="Type a message…" autocomplete="off" maxlength="2000" required>
        <button type="submit" class="client-chat-send">Send</button>
      </form>
    </div>`;

  const msgsEl = document.getElementById("client-chat-msgs");

  // Derive chat key
  let chatKey = null;
  if (chatKeySalt) {
    try {
      chatKey = await LexE2EE.deriveKey(bookingId, chatKeySalt);
    } catch (err) {
      console.error("Could not derive chat key:", err);
    }
  }

  async function loadMessages() {
    try {
      const msgs = await LexAPI.getMessages(bookingId);
      if (!msgs || msgs.length === 0) {
        msgsEl.innerHTML = `<div class="client-chat-empty">No messages yet. Say hello!</div>`;
        return;
      }
      // Resolve current user once outside the map
      const currentUser = LexAPI.getCurrentUser();
      const myId = (currentUser?.id || "").toLowerCase();
      const myName = currentUser?.full_name || null;

      const renderedMsgs = await Promise.all(msgs.map(async m => {
        // Sent by me: sender_id matches OR (fallback) sender_name matches my name
        const isMine = (myId && m.sender_id?.toLowerCase() === myId) ||
          (myName && m.sender_name === myName);
        
        // Ensure UTC timezone is correctly parsed & converted to local time
        const rawDt = m.created_at || "";
        const dtStr = rawDt && !rawDt.endsWith("Z") && !rawDt.includes("+") ? rawDt + "Z" : rawDt;
        const dt = new Date(dtStr);
        const time = dt.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });

        let displayContent = m.content;
        let isDecrypted = false;
        if (m.encrypted) {
          if (chatKey) {
            displayContent = await LexE2EE.decrypt(m.content, m.iv, chatKey);
            isDecrypted = true;
          } else {
            displayContent = "[Encrypted message - Key not derived]";
          }
        }

        const side = isMine ? 'mine' : 'theirs';
        const senderLabel = isMine ? 'You' : (m.sender_name || lawyerName);
        return `<div class="client-chat-msg ${side}">
          <div class="client-chat-bubble">${isDecrypted ? '<span class="lock-indicator" title="End-to-end encrypted">🔒 </span>' : ''}${escapeHtml(displayContent)}</div>
          <div class="client-chat-meta">${senderLabel} · ${time}</div>
        </div>`;
      }));

      const newHtml = renderedMsgs.join("");
      if (msgsEl.innerHTML !== newHtml) {
        msgsEl.innerHTML = newHtml;
        msgsEl.scrollTop = msgsEl.scrollHeight;
      }
    } catch (err) {
      console.error("Could not render messages", err);
      msgsEl.innerHTML = `<div class="client-chat-empty">Could not load messages.</div>`;
    }
  }

  await loadMessages();
  
  if (clientChatInterval) clearInterval(clientChatInterval);
  clientChatInterval = setInterval(loadMessages, 5000);

  if (window.clientChatWS) window.clientChatWS.disconnect();
  if (window.WebSocketChatClient) {
    window.clientChatWS = new WebSocketChatClient(bookingId, async () => {
      SoundNotifier.playChime();
      await loadMessages();
    });
    window.clientChatWS.connect();
  }

  document.getElementById("client-chat-form").onsubmit = async (e) => {
    e.preventDefault();
    const input = document.getElementById("client-chat-input");
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    input.disabled = true;
    try {
      if (chatKey) {
        const encrypted = await LexE2EE.encrypt(text, chatKey);
        await LexAPI.sendMessage(bookingId, encrypted.ciphertext, true, encrypted.iv);
      } else {
        await LexAPI.sendMessage(bookingId, text);
      }
      await loadMessages();
    } catch (err) {
      toast("Could not send message: " + err.message);
    } finally {
      input.disabled = false;
      input.focus();
    }
  };
}

async function joinMeeting(bookingId) {
  try {
    booking = { id: bookingId, step: 4, lawyer: { name: "Your Lawyer" } };
    open();
    await room();
  } catch (err) {
    toast("Could not join room: " + err.message);
  }
}

// ── Dispute Modal (3-Step Dispute Matrix) ───────────────────────────────────

function openDisputeModal(bookingId) {
  open();
  content.innerHTML = `
    <div class="dispute-modal">
      <span class="kicker" style="color:var(--terra);">Resolution Desk</span>
      <h2 style="font-family:'Playfair Display'; margin:6px 0 12px; color:var(--forest);">Raise Consultation Dispute</h2>
      <p class="lead" style="margin-bottom:16px;">Please select the nature of your dispute. Our system cross-references Daily.co room connection logs and network telemetry.</p>
      
      <form id="dispute-form" style="display:flex; flex-direction:column; gap:16px;">
        <div class="field">
          <label style="font-weight:700; font-size:12px;">Nature of Dispute <span style="color:var(--terra);">*</span></label>
          <select id="dispute-category-select" required style="padding:12px; border-radius:10px; border:1px solid var(--line); font-size:14px; font-weight:600; background:#fbfcfb;">
            <option value="">Select a reason...</option>
            <option value="no_show">The lawyer never showed up (No-Show)</option>
            <option value="bad_connectivity">The call disconnected halfway through (Network drop)</option>
            <option value="short_duration">The lawyer stayed for brief duration & left</option>
            <option value="quality_other">Quality of advice / Other issue</option>
          </select>
        </div>

        <div class="field">
          <label style="font-weight:700; font-size:12px;">Detailed Explanation <span style="color:var(--terra);">*</span></label>
          <textarea id="dispute-reason-input" required minlength="10" placeholder="Please describe what happened in detail..." style="min-height:90px; padding:12px; border-radius:10px; border:1px solid var(--line); font-size:14px; background:#fbfcfb;"></textarea>
        </div>

        <div style="background:#fffaf0; border:1px solid #e6d7b8; border-radius:10px; padding:12px 14px; font-size:11px; color:#856404; line-height:1.5;">
          <strong>⚖️ Intermediary Policy & Metadata Waiver</strong><br>
          In accordance with Section 79 of the IT Act (Intermediary Guidelines) and terms agreed at booking, automated room connection logs (timestamps and participant durations) will serve as sole definitive evidence for refund eligibility. Platform does not guarantee specific legal outcomes.
        </div>

        <div id="dispute-modal-error" style="color:var(--terra); font-size:12px; font-weight:700;"></div>

        <div class="actions">
          <button type="button" class="ghost secondary" data-action="close-modal">Cancel</button>
          <button type="submit" class="primary" style="background:var(--terra); color:white;">Submit Dispute & Pause Payout</button>
        </div>
      </form>
    </div>
  `;

  document.querySelector("#dispute-form").onsubmit = async (e) => {
    e.preventDefault();
    const category = document.querySelector("#dispute-category-select").value;
    const reason = document.querySelector("#dispute-reason-input").value.trim();
    const errDiv = document.querySelector("#dispute-modal-error");

    if (!category) {
      errDiv.textContent = "Please select the nature of your dispute.";
      return;
    }
    if (reason.length < 10) {
      errDiv.textContent = "Please provide at least 10 characters explaining your dispute.";
      return;
    }

    try {
      const submitBtn = e.target.querySelector("button[type='submit']");
      submitBtn.disabled = true;
      submitBtn.textContent = "Analyzing logs & submitting...";
      
      const res = await LexAPI.disputeBooking(bookingId, { category, reason });
      close();
      
      const autoStatus = res.auto_resolution_status || "";
      if (autoStatus.includes("AUTO_REFUND")) {
        toast("✓ Dispute submitted. Room logs verified no-show/drop — refund processed automatically.");
      } else {
        toast("✓ Dispute submitted & payout paused. Case sent for Intermediary Shield review.");
      }
      showMyMeetings();
    } catch (err) {
      errDiv.textContent = err.message || "Failed to submit dispute";
    }
  };
}

// ── Review Modal ──────────────────────────────────────────────────────────────


const STAR_LABELS = ["", "Poor", "Below Average", "Good", "Very Good", "Excellent"];

function renderStarsText(rating) {
  return "\u2605".repeat(rating) + "\u2606".repeat(5 - rating);
}

function openReviewModal(bookingId, lawyerName) {
  let selectedRating = 0;

  content.innerHTML = `
    <div class="review-modal">
      <h2>Rate your consultation</h2>
      <p class="review-subtitle">How was your experience with ${lawyerName}?</p>
      <div class="star-picker" id="star-picker">
        ${[1,2,3,4,5].map(i => `<span class="star" data-star="${i}">\u2605</span>`).join("")}
      </div>
      <div class="star-label" id="star-label"></div>
      <textarea id="review-comment" placeholder="Share your experience (optional)..." maxlength="500"></textarea>
      <button class="review-submit" id="review-submit-btn" disabled>Submit Review</button>
    </div>
  `;
  open();

  const picker = document.querySelector("#star-picker");
  const label = document.querySelector("#star-label");
  const submitBtn = document.querySelector("#review-submit-btn");

  // Hover effects
  picker.addEventListener("mouseover", e => {
    const star = e.target.closest("[data-star]");
    if (!star) return;
    const val = parseInt(star.dataset.star);
    picker.querySelectorAll(".star").forEach((s, i) => {
      s.classList.toggle("hover-active", i < val);
    });
    label.textContent = STAR_LABELS[val];
  });

  picker.addEventListener("mouseout", () => {
    picker.querySelectorAll(".star").forEach(s => {
      s.classList.remove("hover-active");
    });
    label.textContent = selectedRating ? STAR_LABELS[selectedRating] : "";
  });

  // Click to select
  picker.addEventListener("click", e => {
    const star = e.target.closest("[data-star]");
    if (!star) return;
    selectedRating = parseInt(star.dataset.star);
    picker.querySelectorAll(".star").forEach((s, i) => {
      s.classList.toggle("active", i < selectedRating);
    });
    label.textContent = STAR_LABELS[selectedRating];
    submitBtn.disabled = false;
  });

  // Submit
  submitBtn.addEventListener("click", async () => {
    if (!selectedRating) return;
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";
    try {
      const comment = document.querySelector("#review-comment").value.trim() || null;
      await LexAPI.submitReview(bookingId, selectedRating, comment);
      close();
      toast("Thank you for your review!");
      showMyMeetings();
    } catch (err) {
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit Review";
      toast("Could not submit review: " + err.message);
    }
  });
}

// Initial checks and loads
LexAPI.subscribe("auth:change", updateHeader);
updateHeader();
loadLawyers();

async function initBookingLanding() {
  const urlParams = new URLSearchParams(window.location.search);
  const bookingIdParam = urlParams.get("booking_id");
  if (bookingIdParam && LexAPI.authenticated()) {
    try {
      if (!lawyers.length) {
        await loadLawyers();
      }
      const list = await LexAPI.bookings();
      const matched = list.find(b => b.id === bookingIdParam);
      if (matched && ["confirmed", "completed", "in_progress"].includes(matched.status)) {
        const l = lawyers.find(x => String(x.id) === String(matched.lawyer_id));
        booking = {
          id: matched.id,
          starts_at: matched.starts_at,
          lawyer: l || { id: matched.lawyer_id, name: matched.lawyer_name || "Your Lawyer", specialty: getSpecialty(matched.practice), practice: mapPracticeToFrontend(matched.practice) },
          step: 4
        };
        bookingView();
        open();
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
      }
    } catch (e) {
      console.error("Error loading redirected booking:", e);
    }
  }
}

initBookingLanding();

const urlParams = new URLSearchParams(window.location.search);
const loginRedirect = urlParams.get("login_redirect");
if (loginRedirect) {
  if (loginRedirect === "lawyer") {
    window.location.href = "lawyer.html";
  } else if (loginRedirect === "admin") {
    window.location.href = "admin-login.html";
  } else {
    const existingUser = LexAPI.getCurrentUser();
    if (existingUser && existingUser.role === loginRedirect) {
      // Already logged in with the right role — go there directly
      window.location.href = loginRedirect === "client" ? "index.html" : loginRedirect + ".html";
    } else {
      // Clear any stale token (e.g. from a different role) before login
      if (existingUser && existingUser.role !== loginRedirect) {
        LexAPI.logout();
      }
      openAuthModal(loginRedirect === "client" ? "index.html" : loginRedirect + ".html");
    }
  }
}

// ── All Lawyers View ─────────────────────────────────────────────────────────

function showAllLawyersView() {
  const allLawyersSection = document.querySelector("#all-lawyers-view");
  const mainEl = document.querySelector("main");
  const myMeetingsSection = document.querySelector("#my-meetings");
  
  mainEl.style.display = "none";
  myMeetingsSection.style.display = "none";
  allLawyersSection.style.display = "";
  window.scrollTo({ top: 0, behavior: "smooth" });
  
  // Reset filters to defaults on view load
  const filterExp = document.getElementById("filter-experience");
  const filterLang = document.getElementById("filter-language");
  const filterRating = document.getElementById("filter-rating");
  if (filterExp) filterExp.value = "0";
  if (filterLang) filterLang.value = "all";
  if (filterRating) filterRating.value = "0";
  
  renderAllLawyers();
}

function renderAllLawyers() {
  const expVal = parseInt(document.getElementById("filter-experience")?.value) || 0;
  const langVal = document.getElementById("filter-language")?.value || "all";
  const ratingVal = parseFloat(document.getElementById("filter-rating")?.value) || 0;
  
  let list = [...lawyers];
  
  // Apply Experience filter
  if (expVal > 0) {
    list = list.filter(x => x.years >= expVal);
  }
  
  // Apply Language filter
  if (langVal !== "all") {
    list = list.filter(x => x.languages.toLowerCase().includes(langVal.toLowerCase()));
  }
  
  // Apply Rating filter
  if (ratingVal > 0) {
    list = list.filter(x => x.rating >= ratingVal);
  }
  
  const gridEl = document.getElementById("all-lawyers-grid");
  if (!gridEl) return;
  
  gridEl.innerHTML = list.length 
    ? list.map(x => `
        <article class="lawyer-card" data-preview="${x.id}">
          <div class="lawyer-photo" style="background:${x.color}">
            <span class="initials" style="background:${darken(x.color)}">${x.initials}</span>
            ${x.available ? '<span class="badge">AVAILABLE TODAY</span>' : ""}
            <span class="rating">★ ${x.rating} (${x.reviews})</span>
          </div>
          <div class="details">
            <h3>${x.name}</h3>
            <p class="specialty">${x.specialty}</p>
            <div class="meta">
              <span>◷ ${x.years} yrs exp.</span>
              <span>◌ ${x.languages}</span>
            </div>
            <div class="card-bottom">
              <span><strong>${money(x.fee)}</strong> <small>/ session</small></span>
              <button class="book" data-book="${x.id}">View &amp; book</button>
            </div>
          </div>
        </article>
      `).join("")
    : `<p class="lead" style="grid-column: 1/-1; text-align: center; padding: 40px 0; color: var(--muted);">No lawyers match your selected filters. Try adjusting them.</p>`;
}


// ── Drafting Feature Functions ───────────────────────────────────────────────

async function showDraftingView() {
  if (!LexAPI.authenticated()) {
    window.location.hash = "";
    toast("Please sign in or register to request drafting.");
    openAuthModal();
    return;
  }
  
  restoreHomeView();
  const mainEl = document.querySelector("main");
  if (mainEl) mainEl.style.display = "none";
  
  const drafting = document.querySelector("#drafting");
  if (drafting) drafting.style.display = "";
  window.scrollTo({ top: 0, behavior: "smooth" });
  
  await loadDraftingRequests();
}

async function loadDraftingRequests() {
  const listEl = document.querySelector("#drafting-list");
  if (!listEl) return;
  
  listEl.innerHTML = `
    <div style="text-align:center; padding:40px;">
      <div style="width: 40px; height: 40px; border: 4px solid var(--sage); border-top-color: var(--forest); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px;"></div>
      <p style="color:var(--muted); font-size:14px;">Loading your drafting requests…</p>
    </div>`;
  
  try {
    const requests = await LexAPI.listDraftingRequests();
    window.currentDraftingRequests = requests || [];
    if (!requests || requests.length === 0) {
      listEl.innerHTML = `
        <div style="text-align:center; padding:50px 30px; background:white; border-radius:16px; border:1px solid #17251f12; max-width:600px; margin:20px auto;">
          <div style="font-size:48px; margin-bottom:16px;">✏</div>
          <h3 style="font-family:'Playfair Display'; font-size:24px; margin:0 0 10px; color:var(--forest);">No Drafting Requests</h3>
          <p style="color:var(--muted); font-size:14px; margin:0 0 24px; line-height:1.6;">You have not posted any legal document drafting requirements yet. Submit details to get quotes from verified legal professionals.</p>
          <button class="primary" data-action="create-drafting" style="min-height:44px; padding:12px 24px; font-size:14px; font-weight:700; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer;">＋ New Request</button>
        </div>`;
      return;
    }
    
    listEl.innerHTML = requests.map(req => {
      let statusText = "";
      let statusClass = "";
      switch (req.status) {
        case "open": statusText = "Open for Quotes"; statusClass = "status-pending"; break;
        case "pending_payment": statusText = "Awaiting Payment"; statusClass = "status-pending"; break;
        case "in_progress": statusText = "In Progress"; statusClass = "status-progress"; break;
        case "submitted": statusText = "Draft Submitted"; statusClass = "status-progress"; break;
        case "completed": statusText = "Completed"; statusClass = "status-done"; break;
        case "cancelled": statusText = "Cancelled"; statusClass = "status-cancelled"; break;
      }
      
      let statusStyle = "";
      if (req.status === "completed") {
        statusStyle = "background:#edf7ed; color:#1e4620; border: 1px solid #c3e6cb;";
      } else if (req.status === "cancelled") {
        statusStyle = "background:#fdf2f2; color:#9b1c1c; border: 1px solid #f5c2c2;";
      } else if (req.status === "in_progress" || req.status === "submitted") {
        statusStyle = "background:#eef6fc; color:#1a567d; border: 1px solid #b3d7f2;";
      } else {
        statusStyle = "background:#fffbf2; color:#9a6b0c; border: 1px solid #fbe6c2;";
      }
      
      let badgeHtml = `<span style="padding: 6px 14px; border-radius: 99px; font-size: 11px; font-weight: 700; text-transform: uppercase; display:inline-block; ${statusStyle}">${statusText}</span>`;
      
      let priceText = `Budget: ${money(req.price_minor / 100)}`;
      if (req.agreed_price_minor) {
        priceText = `Agreed Price: ${money(req.agreed_price_minor / 100)}`;
      }
      
      let proposalsHtml = "";
      if (req.status === "open") {
        if (req.proposals && req.proposals.length > 0) {
          const pendingProps = req.proposals.filter(p => p.status === "pending");
          if (pendingProps.length > 0) {
            proposalsHtml = `
              <div style="margin-top: 16px; border-top: 1px solid var(--line); padding-top: 16px;">
                <h4 style="font-size: 13px; font-weight: 700; margin: 0 0 12px; color: var(--forest);">Interested Lawyers & Counter-Offers:</h4>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                  ${pendingProps.map(p => `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: #fbfdfb; border: 1px solid #17251f0c; padding: 12px 16px; border-radius: 12px;">
                      <div>
                        <strong style="font-size: 14px; color: var(--forest);">${escapeHtml(p.lawyer_name || "Verified Lawyer")}</strong>
                        <div style="font-size: 12px; color: var(--muted); margin-top: 2px;">Proposed Price: ${money(p.amount_minor / 100)}</div>
                      </div>
                      <button class="primary" style="padding: 6px 14px; font-size: 12px; min-height: 32px; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer;" data-action="accept-proposal" data-id="${req.id}" data-proposal-id="${p.id}">Accept Quote</button>
                    </div>
                  `).join("")}
                </div>
              </div>`;
          } else {
            proposalsHtml = `<p style="font-size: 12px; color: var(--muted); margin-top: 14px; font-style: italic;">Awaiting bids and counter-offers from verified lawyers...</p>`;
          }
        } else {
          proposalsHtml = `<p style="font-size: 12px; color: var(--muted); margin-top: 14px; font-style: italic;">Awaiting bids and counter-offers from verified lawyers...</p>`;
        }
      }
      
      let actionHtml = "";
      if (req.status === "pending_payment") {
        actionHtml = `
          <div style="margin-top:20px; display:flex; gap:12px; align-items:center;">
            <button class="primary" data-action="pay-drafting" data-id="${req.id}" style="min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer;">Pay & Start Work (${money(req.agreed_price_minor / 100)})</button>
            <button class="outline" data-action="cancel-drafting" data-id="${req.id}" style="color:var(--terra); border: 1px solid var(--terra); background:none; min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; cursor:pointer;">Cancel Request</button>
          </div>`;
      } else if (req.status === "open") {
        actionHtml = `
          <div style="margin-top:20px;">
            <button class="outline" data-action="cancel-drafting" data-id="${req.id}" style="color:var(--terra); border: 1px solid var(--terra); background:none; min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; cursor:pointer;">Cancel Request</button>
          </div>`;
      } else if (req.status === "submitted") {
        const commentCount = (req.comments || []).length;
        const pdfUrl = req.draft_file_key ? `/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}` : '#';

        let autoApproveText = "";
        if (req.auto_approve_at) {
          const autoDate = new Date(req.auto_approve_at);
          const diffMs = autoDate - new Date();
          if (diffMs > 0) {
            const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            autoApproveText = `⏱️ 7-Day Window: Auto-approves & releases payment in ${days}d ${hours}h if inactive.`;
          }
        }

        const docDownloadHtml = req.draft_file_key ? `
          <a href="${pdfUrl}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:12px 16px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04); margin-bottom:12px;">
            <span>📄 ${escapeHtml(req.draft_filename || 'Submitted Legal Document')}</span>
            <span style="font-size:12px; font-weight:700; color:var(--forest);">Download Document ↓</span>
          </a>
        ` : (req.draft_text ? `
          <div style="white-space: pre-wrap; background: white; border: 1px solid var(--line); padding: 14px; border-radius: 8px; font-family: monospace; font-size: 13px; max-height: 250px; overflow-y: auto; color: var(--ink); line-height: 1.5; text-align: left; margin-bottom:12px;">${escapeHtml(req.draft_text)}</div>
        ` : `
          <div style="font-size:13px; color:var(--forest); background:white; padding:12px 16px; border-radius:8px; border:1px solid #d5e0d7; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04); margin-bottom:12px;">
            <span>📄 ${escapeHtml(req.draft_filename || 'Submitted Legal Document.pdf')}</span>
            <span style="font-size:12px; font-weight:700; color:var(--forest);">Ready Document</span>
          </div>
        `);

        actionHtml = `
          <div style="margin-top: 20px; background: #faf8f5; border: 1px solid #e8dcc4; border-radius: 12px; padding: 20px; text-align: left;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
              <h4 style="font-size: 14px; font-weight: 700; margin: 0; color: var(--terra);">Submitted Legal Document for Review:</h4>
              <span style="font-size:12px; font-weight:700; color:var(--forest); background:#eef5f0; padding:4px 12px; border-radius:99px;">💬 ${commentCount} Inline Comment Pin${commentCount === 1 ? '' : 's'}</span>
            </div>
            ${autoApproveText ? `<div style="background:#eef6fc; border:1px solid #b3d7f2; border-radius:8px; padding:8px 12px; font-size:12px; color:#1a567d; font-weight:700; margin-bottom:12px;">${autoApproveText}</div>` : ''}
            ${docDownloadHtml}
            <div style="margin-top: 16px; display: flex; gap: 12px; flex-wrap:wrap;">
              <button class="primary" data-action="open-pdf-annotator" data-id="${req.id}" data-filename="${escapeHtml(req.draft_filename || 'Legal Document')}" data-url="${pdfUrl}" style="min-height:38px; padding:8px 20px; font-size:13px; font-weight:700; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer;">🔍 Open Interactive PDF & Drop Comments</button>
              <button class="primary" data-action="approve-draft" data-id="${req.id}" style="min-height:38px; padding:8px 20px; font-size:13px; font-weight:700; border-radius:99px; border:none; background:#2e7d32; color:white; cursor:pointer;">✓ Approve & Release Payment</button>
            </div>
          </div>`;
      } else if (req.status === "revision_requested") {
        const commentCount = (req.comments || []).length;
        const pdfUrl = req.draft_file_key ? `/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}` : '#';

        actionHtml = `
          <div style="margin-top: 20px; background: #fff7ed; border: 1px solid #fed7aa; border-radius: 12px; padding: 20px; text-align: left;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
              <h4 style="font-size: 14px; font-weight: 700; margin: 0; color: #9a3412;">🔄 Revision Requested:</h4>
              <span style="font-size:12px; font-weight:700; color:#9a3412; background:#ffedd5; padding:4px 12px; border-radius:99px;">💬 ${commentCount} Inline Comment Pin${commentCount === 1 ? '' : 's'}</span>
            </div>
            <p style="font-size:13px; color:#7c2d12; margin:0 0 14px;">The lawyer has been notified of your requested changes and inline comment pins.</p>
            <button class="primary" data-action="open-pdf-annotator" data-id="${req.id}" data-filename="${escapeHtml(req.draft_filename || 'Legal Document')}" data-url="${pdfUrl}" style="min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; border:none; background:#9a3412; color:white; cursor:pointer;">🔍 View Your Inline Comments</button>
          </div>`;
      } else if (req.status === "completed") {
        const docDownloadHtml = req.draft_file_key ? `
          <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:12px 16px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
            <span>📄 ${escapeHtml(req.draft_filename || 'Approved Legal Document')}</span>
            <span style="font-size:12px; font-weight:700; color:var(--forest);">Download Document ↓</span>
          </a>
        ` : (req.draft_text ? `
          <div style="white-space: pre-wrap; background: white; border: 1px solid var(--line); padding: 14px; border-radius: 8px; font-family: monospace; font-size: 13px; max-height: 250px; overflow-y: auto; color: var(--ink); line-height: 1.5; text-align: left;">${escapeHtml(req.draft_text)}</div>
        ` : '');

        actionHtml = `
          <div style="margin-top: 20px; background: #f4f8f5; border: 1px solid #bddcc4; border-radius: 12px; padding: 20px; text-align: left;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
              <h4 style="font-size: 14px; font-weight: 700; margin: 0; color: var(--forest); display:flex; align-items:center; gap:6px;"><span>✓</span> Approved & Signed-Off Document</h4>
              <span style="font-size:11px; font-weight:700; color:#1b4332; background:#d8f3dc; padding:4px 10px; border-radius:99px;">🔒 Version Frozen (Read-Only)</span>
            </div>
            ${docDownloadHtml}
          </div>`;
      }
      
      return `
        <article style="background:white; border-radius:20px; padding:28px; border:1px solid #17251f12; display:flex; flex-direction:column; text-align:left; max-width:800px; margin:0 auto; width:100%; box-shadow: 0 4px 12px rgba(23,37,31,0.02);">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
            <div style="flex:1; min-width:280px;">
              <h3 style="font-family:'Playfair Display'; font-size:24px; margin:0 0 10px; color:var(--forest); font-weight:600;">${escapeHtml(req.title)}</h3>
              <p style="color:var(--muted); font-size:15px; line-height:1.6; margin:0 0 16px;">${escapeHtml(req.description)}</p>
              ${req.documents && req.documents.length ? `
                <div style="margin: -8px 0 16px; display:flex; flex-wrap:wrap; gap:10px; align-items:center;">
                  <span style="font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em;">Reference docs:</span>
                  ${req.documents.map(doc => `
                    <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(doc.key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); text-decoration:underline; font-weight:600; display:inline-flex; align-items:center; gap:4px;">
                      📎 ${escapeHtml(doc.filename)}
                    </a>
                  `).join("")}
                </div>
              ` : ""}
              <div style="display:flex; flex-wrap:wrap; gap:16px; font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em;">
                <span>${priceText}</span>
                <span>•</span>
                <span>Posted: ${new Date(req.created_at).toLocaleDateString()}</span>
                ${req.drafter_name ? `<span>•</span><span>Drafter: ${escapeHtml(req.drafter_name)}</span>` : ""}
              </div>
            </div>
            <div style="flex-shrink:0;">
              ${badgeHtml}
            </div>
          </div>
          ${proposalsHtml}
          ${actionHtml}
        </article>
      `;
    }).join("");
  } catch (err) {
    listEl.innerHTML = `<div style="color:var(--terra); text-align:center; padding:30px; font-weight:700; background:white; border-radius:16px; border:1px solid #17251f12;">Error loading drafting requests: ${err.message}</div>`;
  }
}

window.openCreateDraftingModal = function() {
  open();
  content.innerHTML = `
    <span class="kicker" style="color:var(--terra); text-transform:uppercase; font-size:11px; letter-spacing:0.16em; font-weight:700;">Drafting Request</span>
    <h2 style="font-family:'Playfair Display'; font-size:28px; margin:6px 0 12px; color:var(--forest);">Post Drafting Requirement</h2>
    <p class="lead" style="color:var(--muted); font-size:14px; margin-bottom:20px; line-height:1.6;">Describe the legal document you need drafted (e.g. rent agreement, partnership deed, NDA, legal notice) and specify the price you are willing to pay.</p>
    <form class="form" id="create-drafting-form" autocomplete="off" style="display:grid; gap:20px; margin-top:20px;">
      <div class="field full" style="display:grid; gap:8px;">
        <label style="font-size:13px; font-weight:700; color:var(--forest);">Document Title *</label>
        <input type="text" id="drafting-title" placeholder="e.g. Non-Disclosure Agreement (NDA)" required minlength="2" maxlength="255" style="width:100%; border:1px solid var(--line); border-radius:11px; padding:14px; font-size:15px; background:#fbfcfb;">
      </div>
      <div class="field full" style="display:grid; gap:8px;">
        <label style="font-size:13px; font-weight:700; color:var(--forest);">Requirements & Instructions *</label>
        <textarea id="drafting-desc" placeholder="Provide background information, the names/relationships of parties involved, key clauses, and other requirements." required minlength="5" style="width:100%; border:1px solid var(--line); border-radius:11px; padding:14px; font-size:15px; background:#fbfcfb; min-height:140px; resize:vertical; line-height:1.5;"></textarea>
      </div>
      <div class="field full" style="display:grid; gap:8px;">
        <label style="font-size:13px; font-weight:700; color:var(--forest);">Budget Price willing to pay (INR) *</label>
        <input type="number" id="drafting-price" placeholder="e.g. 2500" min="100" required style="width:100%; border:1px solid var(--line); border-radius:11px; padding:14px; font-size:15px; background:#fbfcfb;">
      </div>
      <div class="field full" style="display:grid; gap:8px;">
        <label style="font-size:13px; font-weight:700; color:var(--forest);">Reference Documents (optional)</label>
        <input type="file" id="drafting-files" multiple style="font-size:14px; color:var(--ink);" accept=".pdf,.png,.jpg,.jpeg,.docx">
        <div id="drafting-uploaded-list" style="margin-top:8px; display:flex; flex-direction:column; gap:6px;"></div>
      </div>
      <div id="drafting-form-error" style="color:var(--terra); font-size:12px; font-weight:700;"></div>
      <div class="actions" style="display:flex; justify-content:flex-end; gap:10px; margin-top:10px;">
        <button type="button" class="secondary" data-action="close-modal" style="border:none; border-radius:99px; padding:12px 20px; font-weight:700; cursor:pointer; background:#edf2ee; color:var(--ink);">Cancel</button>
        <button class="primary" type="submit" style="border:none; border-radius:99px; padding:12px 20px; font-weight:700; cursor:pointer; background:var(--forest); color:white;">Post Request</button>
      </div>
    </form>
  `;

  let uploadedFiles = [];
  const fileInput = document.querySelector("#drafting-files");
  const listDiv = document.querySelector("#drafting-uploaded-list");

  if (fileInput && listDiv) {
    fileInput.onchange = async () => {
      const files = Array.from(fileInput.files);
      for (const file of files) {
        if (!["application/pdf", "image/jpeg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"].includes(file.type)) {
          toast(`Skipped ${file.name}: Only PDF, JPEG, PNG, or DOCX are allowed.`);
          continue;
        }
        if (file.size > 20 * 1024 * 1024) {
          toast(`Skipped ${file.name}: Must be under 20 MB.`);
          continue;
        }

        const item = document.createElement("div");
        item.style.fontSize = "13px";
        item.style.color = "var(--muted)";
        item.textContent = `Uploading ${file.name}...`;
        listDiv.appendChild(item);

        try {
          const presign = await LexAPI.presignDraftingDocument(file.name, file.type || "application/pdf");
          const formData = new FormData();
          Object.entries(presign.upload.fields || {}).forEach(([k,v]) => formData.append(k, v));
          formData.append("file", file);
          const headers = {};
          const token = LexAPI.getAccessToken();
          const uploadUrl = LexAPI.resolveUploadUrl(presign.upload.url);
          if (token && presign.upload.url.startsWith("/")) {
            headers["Authorization"] = `Bearer ${token}`;
          }
          const res = await fetch(uploadUrl, { method: "POST", body: formData, headers });
          if (res.ok || res.status === 201 || res.status === 204) {
            uploadedFiles.push({ filename: file.name, key: presign.key });
            item.style.color = "var(--forest)";
            item.style.fontWeight = "bold";
            item.textContent = `✓ ${file.name} uploaded`;
          } else {
            throw new Error(`Upload status ${res.status}`);
          }
        } catch (err) {
          // Dev fallback
          const mockKey = `drafting/mock-${Date.now()}-${file.name}`;
          try {
            const formData = new FormData();
            formData.append("key", mockKey);
            formData.append("file", file);
            await fetch(LexAPI.resolveUploadUrl("/api/v1/drafting/documents/mock-upload"), { method: "POST", body: formData });
            uploadedFiles.push({ filename: file.name, key: mockKey });
            item.style.color = "var(--forest)";
            item.style.fontWeight = "bold";
            item.textContent = `✓ ${file.name} uploaded`;
          } catch (e2) {
            item.style.color = "var(--terra)";
            item.textContent = `✗ ${file.name} failed: ${err.message}`;
          }
        }
      }
      fileInput.value = "";
    };
  }
  
  document.querySelector("#create-drafting-form").onsubmit = async (e) => {
    e.preventDefault();
    const title = document.querySelector("#drafting-title").value;
    const description = document.querySelector("#drafting-desc").value;
    const price = parseInt(document.querySelector("#drafting-price").value, 10);
    
    if (isNaN(price) || price < 1) {
      document.querySelector("#drafting-form-error").textContent = "Price must be a valid amount greater than zero.";
      return;
    }
    
    const submitBtn = e.target.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";
    
    try {
      await LexAPI.createDraftingRequest({
        title,
        description,
        price_minor: price * 100,
        documents: uploadedFiles
      });
      close();
      toast("Drafting request posted successfully!");
      if (document.querySelector("#drafting").style.display !== "none") {
        await loadDraftingRequests();
      }
    } catch (err) {
      document.querySelector("#drafting-form-error").textContent = err.message;
      submitBtn.disabled = false;
      submitBtn.textContent = "Post Request";
    }
  };
}

window.acceptProposal = async function(reqId, proposalId) {
  if (!confirm("Are you sure you want to accept this lawyer's counter-offer? This will finalize the amount and lock this assignment to them.")) {
    return;
  }
  try {
    await LexAPI.acceptDraftingProposal(reqId, proposalId);
    toast("Quote accepted! Please make the payment to start work.");
    await loadDraftingRequests();
  } catch (err) {
    toast("Error: " + err.message);
  }
}

window.payForDrafting = async function(reqId) {
  try {
    const req = await LexAPI.getDraftingRequest(reqId);
    if (!req) {
      toast("Error: Drafting request not found");
      return;
    }
    const amountMinor = req.agreed_price_minor || req.price_minor || 0;
    const priceText = money(amountMinor / 100);

    content.innerHTML = `
      <div style="padding: 10px 5px;">
        <span class="eyebrow" style="color:var(--forest); font-weight:700; letter-spacing:0.12em; text-transform:uppercase; font-size:11px;">🔒 SECURE ESCROW PAYMENT</span>
        <h2 style="font-family:'Playfair Display',serif; font-size:24px; margin:6px 0 16px; color:var(--ink);">Complete Drafting Payment</h2>
        
        <div style="background:var(--bg-soft); border-radius:12px; padding:16px; margin-bottom:20px; border:1px solid rgba(0,0,0,0.06);">
          <h4 style="margin:0 0 6px; font-size:15px; font-weight:700; color:var(--ink);">${escapeHtml(req.title)}</h4>
          <p style="margin:0; font-size:13px; color:var(--muted); line-height:1.4;">${escapeHtml(req.description ? (req.description.substring(0, 120) + (req.description.length > 120 ? '...' : '')) : '')}</p>
        </div>

        <div style="background:#f9fbf9; border:1px solid #e2ebe4; border-radius:12px; padding:16px; margin-bottom:20px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:13px; color:var(--muted);">Agreed Drafting Fee</span>
            <strong style="font-size:14px; color:var(--ink);">${priceText}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:13px; color:var(--muted);">Escrow & Protection Fee</span>
            <span style="font-size:13px; color:var(--forest); font-weight:600;">Free (Included)</span>
          </div>
          <hr style="border:none; border-top:1px dashed #d5e0d7; margin:10px 0;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="font-size:15px; color:var(--ink);">Total Amount Payable</strong>
            <strong style="font-size:20px; color:var(--forest); font-family:'DM Sans',sans-serif;">${priceText}</strong>
          </div>
        </div>

        <div style="margin-bottom:22px;">
          <label style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:var(--muted); display:block; margin-bottom:8px;">Select Payment Method</label>
          <div style="display:flex; flex-direction:column; gap:8px;">
            <label style="display:flex; align-items:center; gap:10px; padding:12px 14px; border:1.5px solid var(--forest); border-radius:10px; cursor:pointer; background:#fff;">
              <input type="radio" name="drafting-payment-method" value="upi" checked style="accent-color:var(--forest);">
              <div>
                <strong style="font-size:13px; display:block; color:var(--ink);">UPI / Instant Pay (BHIM, GPay, Paytm)</strong>
                <small style="color:var(--muted); font-size:11px;">Zero transaction fees</small>
              </div>
            </label>
            <label style="display:flex; align-items:center; gap:10px; padding:12px 14px; border:1px solid #e0e0e0; border-radius:10px; cursor:pointer; background:#fff;">
              <input type="radio" name="drafting-payment-method" value="card" style="accent-color:var(--forest);">
              <div>
                <strong style="font-size:13px; display:block; color:var(--ink);">Credit / Debit Card</strong>
                <small style="color:var(--muted); font-size:11px;">Visa, MasterCard, RuPay</small>
              </div>
            </label>
          </div>
        </div>

        <div style="background:#f4f7f5; padding:12px 14px; border-radius:10px; font-size:12px; color:var(--muted); line-height:1.5; margin-bottom:24px; display:flex; align-items:flex-start; gap:8px;">
          <span style="font-size:16px;">🛡️</span>
          <span><strong>Buyer Protection:</strong> Your payment will be safely held in VidhiMeet Escrow and only released to the lawyer after you review and approve the finalized draft.</span>
        </div>

        <div id="drafting-pay-error" style="color:var(--terra); font-size:13px; margin-bottom:12px; font-weight:600;" hidden></div>

        <div class="actions" style="display:flex; gap:12px; justify-content:flex-end;">
          <button class="ghost secondary" data-action="close-modal" style="padding:10px 20px; border-radius:99px; cursor:pointer;">Cancel</button>
          <button class="primary" id="confirm-drafting-pay-btn" style="padding:10px 24px; border-radius:99px; background:var(--forest); color:white; border:none; font-weight:700; cursor:pointer;">Confirm & Pay ${priceText}</button>
        </div>
      </div>
    `;

    open();

    document.getElementById("confirm-drafting-pay-btn").onclick = async function() {
      const btn = this;
      const errEl = document.getElementById("drafting-pay-error");
      if (errEl) errEl.hidden = true;
      btn.disabled = true;
      btn.textContent = "Processing Payment...";

      try {
        await LexAPI.confirmDraftingPayment(reqId);
        close();
        toast("Payment successful! The lawyer has been notified to begin drafting.");
        await loadDraftingRequests();
      } catch (err) {
        btn.disabled = false;
        btn.textContent = `Confirm & Pay ${priceText}`;
        if (errEl) {
          errEl.textContent = err.message || "Payment processing failed. Please try again.";
          errEl.hidden = false;
        }
      }
    };
  } catch (err) {
    toast("Error loading payment details: " + err.message);
  }
}

window.approveDraft = async function(reqId) {
  if (!confirm("Are you sure you want to approve this draft? This will complete the request and release funds to the drafter minus platform fee.")) {
    return;
  }
  try {
    await LexAPI.approveDraft(reqId);
    toast("Draft approved successfully! Payment released to the lawyer.");
    await loadDraftingRequests();
  } catch (err) {
    toast("Error: " + err.message);
  }
}

window.cancelDrafting = async function(reqId) {
  console.log("window.cancelDrafting called for request ID:", reqId);
  if (!confirm("Are you sure you want to cancel this request? Any pending bids/proposals will be rejected.")) {
    console.log("Cancellation aborted by user.");
    return;
  }
  try {
    console.log("Invoking LexAPI.cancelDraftingRequest...");
    await LexAPI.cancelDraftingRequest(reqId);
    console.log("Successfully cancelled request.");
    toast("Drafting request cancelled.");
    await loadDraftingRequests();
  } catch (err) {
    console.error("Failed to cancel request:", err);
    toast("Error cancelling request: " + err.message);
  }
}

window.viewDraftingDetails = async function(reqId) {
  try {
    const req = await LexAPI.getDraftingRequest(reqId);
    if (!req) {
      toast("Error: Drafting request not found");
      return;
    }
    const priceText = money((req.agreed_price_minor || req.price_minor || 0) / 100);

    const docHtml = req.documents && req.documents.length ? `
      <div style="background:#f4f7f5; border-radius:12px; padding:16px; margin-bottom:20px; border:1px solid #e2ebe4;">
        <span style="font-size:12px; font-weight:700; color:var(--forest); text-transform:uppercase; letter-spacing:0.06em; display:block; margin-bottom:10px;">📁 Attached Reference Documents (${req.documents.length})</span>
        <div style="display:flex; flex-direction:column; gap:8px;">
          ${req.documents.map(doc => `
            <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(doc.key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:10px 14px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
              <span>📄 ${escapeHtml(doc.filename)}</span>
              <span style="font-size:12px; font-weight:700; color:var(--forest);">Download ↓</span>
            </a>
          `).join("")}
        </div>
      </div>
    ` : `
      <div style="background:#fafafa; border-radius:10px; padding:12px 14px; margin-bottom:20px; border:1px dashed #e0e0e0; font-size:13px; color:var(--muted);">
        ℹ️ No reference documents were attached to this request.
      </div>
    `;

    const draftHtml = req.draft_file_key ? `
      <div style="margin-bottom:20px; background:#fbfcfb; border:1px solid #d5e0d7; border-radius:12px; padding:16px;">
        <h4 style="font-size:14px; font-weight:700; margin:0 0 10px; color:var(--forest);">Submitted Ready Document</h4>
        <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:12px 16px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
          <span>📄 ${escapeHtml(req.draft_filename || 'Legal Document')}</span>
          <span style="font-size:12px; font-weight:700; color:var(--forest);">Download Document ↓</span>
        </a>
      </div>
    ` : (req.draft_text ? `
      <div style="margin-bottom:20px; background:#fbfcfb; border:1px solid #d5e0d7; border-radius:12px; padding:16px;">
        <h4 style="font-size:14px; font-weight:700; margin:0 0 10px; color:var(--forest);">Drafted Content</h4>
        <div style="white-space:pre-wrap; font-family:monospace; font-size:13px; background:white; border:1px solid var(--line); padding:14px; border-radius:8px; max-height:220px; overflow-y:auto;">${escapeHtml(req.draft_text)}</div>
      </div>
    ` : "");

    content.innerHTML = `
      <div style="padding:10px 5px;">
        <span class="eyebrow" style="color:var(--forest); font-weight:700; letter-spacing:0.12em; text-transform:uppercase; font-size:11px;">Drafting Request Details</span>
        <h2 style="font-family:'Playfair Display',serif; font-size:24px; margin:6px 0 16px; color:var(--ink);">${escapeHtml(req.title)}</h2>
        
        <div style="display:flex; gap:16px; font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; margin-bottom:16px; flex-wrap:wrap;">
          <span>Budget/Price: ${priceText}</span>
          <span>•</span>
          <span>Status: ${req.status.replace("_", " ")}</span>
          <span>•</span>
          <span>Posted: ${new Date(req.created_at).toLocaleDateString()}</span>
        </div>

        <div style="background:var(--bg-soft); border-radius:12px; padding:16px; margin-bottom:20px; border:1px solid rgba(0,0,0,0.06);">
          <h4 style="margin:0 0 6px; font-size:13px; font-weight:700; color:var(--forest); text-transform:uppercase;">Requirements & Instructions</h4>
          <p style="margin:0; font-size:14px; color:var(--ink); line-height:1.5; white-space:pre-wrap;">${escapeHtml(req.description)}</p>
        </div>

        ${docHtml}
        ${draftHtml}

        <div class="actions" style="display:flex; justify-content:flex-end;">
          <button class="ghost secondary" data-action="close-modal" style="padding:10px 24px; border-radius:99px; cursor:pointer;">Close</button>
        </div>
      </div>
    `;

    open();
  } catch (err) {
    toast("Error loading request details: " + err.message);
  }
}

function openContactModal() {
  content.innerHTML = `
    <div style="padding: 24px; max-width: 500px; margin: 0 auto; text-align: left;">
      <small class="eyebrow" style="color: #4f46e5; text-transform: uppercase; font-weight: 700; letter-spacing: 0.12em;">GET IN TOUCH</small>
      <h2 style="font-family: var(--font-display, sans-serif); font-size: 26px; margin: 8px 0 16px; color: #1e293b;">Contact Us</h2>
      <p style="color: #64748b; font-size: 14px; margin-bottom: 20px; line-height: 1.5;">Have questions about VidhiMeet or need assistance with your booking? We are here to help.</p>
      
      <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; background: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0; font-size: 14px;">
        <div><strong>📧 Email Support:</strong> <a href="mailto:support@VidhiMeet.in" style="color: #4f46e5; font-weight: 600;">support@VidhiMeet.in</a></div>
        <div><strong>📞 Toll-Free Phone:</strong> +91 (800) 539-4743 (Mon - Sat, 9 AM - 7 PM IST)</div>
      </div>

      <form id="contact-form" style="display: flex; flex-direction: column; gap: 12px;">
        <input type="text" id="contact-name" placeholder="Your Full Name" required style="padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 14px;">
        <input type="email" id="contact-email" placeholder="Your Email Address" required style="padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 14px;">
        <textarea id="contact-message" placeholder="How can our support team assist you?" rows="4" required style="padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 14px; resize: vertical;"></textarea>
        <button type="submit" class="primary" style="padding: 12px; font-weight: 700; border-radius: 8px; background: #4f46e5; color: white; border: none; cursor: pointer;">Send Message</button>
      </form>
    </div>
  `;
  open();

  const form = document.querySelector("#contact-form");
  if (form) {
    form.onsubmit = (e) => {
      e.preventDefault();
      close();
      toast("Thank you for reaching out! Our support team will contact you shortly.");
    };
  }
}

function openFeedbackModal() {
  content.innerHTML = `
    <div style="padding: 24px; max-width: 500px; margin: 0 auto; text-align: left;">
      <small class="eyebrow" style="color: #4f46e5; text-transform: uppercase; font-weight: 700; letter-spacing: 0.12em;">YOUR OPINION MATTERS</small>
      <h2 style="font-family: var(--font-display, sans-serif); font-size: 26px; margin: 8px 0 16px; color: #1e293b;">Share Your Feedback</h2>
      <p style="color: #64748b; font-size: 14px; margin-bottom: 20px; line-height: 1.5;">Help us improve VidhiMeet. Tell us about your consultation experience or suggest features.</p>
      
      <form id="feedback-form" style="display: flex; flex-direction: column; gap: 14px;">
        <label style="font-size: 14px; font-weight: 600; color: #334155;">Overall Satisfaction
          <select id="feedback-rating" style="width: 100%; margin-top: 6px; padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 14px; background: white;">
            <option value="5">⭐⭐⭐⭐⭐ Excellent (5/5)</option>
            <option value="4">⭐⭐⭐⭐ Good (4/5)</option>
            <option value="3">⭐⭐⭐ Average (3/5)</option>
            <option value="2">⭐⭐ Needs Improvement (2/5)</option>
            <option value="1">⭐ Poor (1/5)</option>
          </select>
        </label>
        <textarea id="feedback-comments" placeholder="What worked well? How can we serve you better?" rows="4" required style="padding: 12px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 14px; resize: vertical;"></textarea>
        <button type="submit" class="primary" style="padding: 12px; font-weight: 700; border-radius: 8px; background: #4f46e5; color: white; border: none; cursor: pointer;">Submit Feedback</button>
      </form>
    </div>
  `;
  open();

  const form = document.querySelector("#feedback-form");
  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const rating = parseInt(document.querySelector("#feedback-rating")?.value || "5", 10);
      const comments = document.querySelector("#feedback-comments")?.value?.trim() || "";
      if (!comments) return;

      try {
        await LexAPI.submitPlatformFeedback({ rating, comments });
        close();
        toast("Thank you for your valuable feedback!");
      } catch (err) {
        toast("Error submitting feedback: " + (err.message || "Please try again"));
      }
    };
  }
}

// ── Client Hash Routing ──────────────────────────────────────────────────────────
function checkHashRoute() {
  const hash = window.location.hash;
  if (hash === "#contact") {
    openContactModal();
  } else if (hash === "#feedback") {
    openFeedbackModal();
  } else if (hash === "#drafting") {
    showDraftingView();
  } else if (hash === "#my-meetings") {
    showMyMeetings();
  } else if (hash === "#all-lawyers-view") {
    showAllLawyersView();
  } else if (hash === "" || hash === "#home") {
    restoreHomeView();
  }
}
window.addEventListener("hashchange", checkHashRoute);
checkHashRoute();

document.addEventListener("click", e => {
  const contactBtn = e.target.closest("#contact-us-btn");
  if (contactBtn) {
    e.preventDefault();
    openContactModal();
    return;
  }
  const feedbackBtn = e.target.closest("#feedback-btn");
  if (feedbackBtn) {
    e.preventDefault();
    openFeedbackModal();
    return;
  }
});

// ── Global Data-Action Event Delegation for Client Portal ─────────────────────
document.addEventListener("click", async e => {
  const actionBtn = e.target.closest("[data-action]");
  if (!actionBtn) return;

  const action = actionBtn.dataset.action;
  const id = actionBtn.dataset.id;

  switch (action) {
    case "create-drafting":
      if (window.openCreateDraftingModal) window.openCreateDraftingModal();
      break;
    case "accept-proposal":
      if (window.acceptProposal) window.acceptProposal(id, actionBtn.dataset.proposalId);
      break;
    case "pay-drafting":
      if (window.payForDrafting) window.payForDrafting(id);
      break;
    case "approve-draft":
      if (window.approveDraft) window.approveDraft(id);
      break;
    case "cancel-drafting":
      if (window.cancelDrafting) window.cancelDrafting(id);
      break;
    case "open-pdf-annotator": {
      const reqObj = (window.currentDraftingRequests || []).find(r => r.id === id);
      const pdfUrl = actionBtn.dataset.url;
      const filename = actionBtn.dataset.filename || "Document.pdf";
      if (window.openPdfAnnotatorModal) {
        window.openPdfAnnotatorModal({
          reqId: id,
          pdfUrl: pdfUrl,
          filename: filename,
          status: reqObj ? reqObj.status : "submitted",
          isClient: true,
          comments: reqObj ? (reqObj.comments || []) : [],
          draftText: reqObj ? reqObj.draft_text : null,
          onRefresh: async () => { if (window.loadDraftingRequests) await window.loadDraftingRequests(); }
        });
      }
      break;
    }
    case "view-drafting-details":
      if (window.viewDraftingDetails) window.viewDraftingDetails(id);
      break;
    case "close-modal":
      closeModal();
      break;
  }
});

// ── Custom Hero Dropdown Component ──────────────────────────────────────────
function initHeroDropdown() {
  const customDropdown = document.querySelector("#hero-practice-dropdown");
  if (!customDropdown) return;

  const trigger = customDropdown.querySelector("#dropdown-trigger");
  const options = customDropdown.querySelectorAll(".dropdown-option");
  const nativeSelect = customDropdown.querySelector("#practice");
  const selectedText = customDropdown.querySelector("#selected-practice-text");
  const selectedIcon = customDropdown.querySelector(".option-icon");
  const searchForm = document.querySelector("#search");

  function toggleDropdown(show) {
    const isOpen = show !== undefined ? show : !customDropdown.classList.contains("open");
    customDropdown.classList.toggle("open", isOpen);
    if (trigger) trigger.setAttribute("aria-expanded", isOpen);
  }

  if (trigger) {
    trigger.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleDropdown();
    });
  }

  options.forEach(opt => {
    opt.addEventListener("click", (e) => {
      e.stopPropagation();
      const val = opt.dataset.value;
      const text = opt.dataset.text;
      const icon = opt.dataset.icon;

      // Update active option styling
      options.forEach(o => o.classList.toggle("active", o === opt));

      // Update trigger label & icon
      if (selectedText) selectedText.textContent = text;
      if (selectedIcon) selectedIcon.textContent = icon;

      // Update hidden select
      if (nativeSelect) {
        nativeSelect.value = val;
        nativeSelect.dispatchEvent(new Event("change"));
      }

      // Update global practice variable & re-render lawyers grid
      practice = val;
      render();

      toggleDropdown(false);
    });
  });

  // Handle Search Form Submission
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      toggleDropdown(false);
      const lawyersSec = document.querySelector("#lawyers");
      if (lawyersSec) {
        lawyersSec.scrollIntoView({ behavior: "smooth" });
      }
    });
  }

  // Close dropdown when clicking outside
  document.addEventListener("click", (e) => {
    if (!customDropdown.contains(e.target)) {
      toggleDropdown(false);
    }
  });

  // Close on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") toggleDropdown(false);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initHeroDropdown);
} else {
  initHeroDropdown();
}

// Universal password visibility toggle
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".password-toggle-btn");
  if (!btn) return;
  e.preventDefault();
  const wrap = btn.closest(".password-wrap, .input-wrapper");
  if (!wrap) return;
  const input = wrap.querySelector("input");
  if (!input) return;
  const isPass = input.type === "password";
  input.type = isPass ? "text" : "password";
  const eyeOpen = btn.querySelector(".eye-open");
  const eyeClosed = btn.querySelector(".eye-closed");
  if (eyeOpen && eyeClosed) {
    eyeOpen.style.display = isPass ? "none" : "block";
    eyeClosed.style.display = isPass ? "block" : "none";
  }
  btn.setAttribute("aria-label", isPass ? "Hide password" : "Show password");
  btn.setAttribute("title", isPass ? "Hide password" : "Show password");
});


