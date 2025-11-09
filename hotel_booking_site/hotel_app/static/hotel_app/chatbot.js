let hotels = [];

// Load CSV hotel data
fetch("hotels.csv")
  .then(res => res.text())
  .then(data => {
    const rows = data.split("\n").slice(1);
    hotels = rows.map(row => {
      const [hotel_name, city, price, stars] = row.split(",");
      return { hotel_name, city, price, stars };
    });
  });

// Send message
function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const msg = input.value.trim();
  if (!msg) return;

  chatBox.innerHTML += `<div class="user-message">${msg}</div>`;
  input.value = "";

  let reply = getBotReply(msg.toLowerCase());
  setTimeout(() => {
    chatBox.innerHTML += `<div class="bot-message">${reply}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  }, 400);
}

// Bot logic
function getBotReply(message) {
  let cityHotels = hotels.filter(h => message.includes(h.city?.toLowerCase()));
  if (cityHotels.length > 0) {
    let reply = `✅ ${capitalize(cityHotels[0].city)} me ${cityHotels.length} hotels mil gaye:<br>`;
    cityHotels.forEach(h => {
      reply += `🏨 <b>${h.hotel_name}</b> — ₹${h.price}/night (${h.stars}-Star)<br>`;
    });
    return reply;
  } else if (message.includes("hello") || message.includes("hi")) {
    return "Hello bhai 👋! MP me kis city ke hotels dekhna chahoge?";
  } else {
    return "❌ Bhai ye city MP me nahi mili. Try likhna: Bhopal, Indore, Jabalpur...";
  }
}

function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.slice(1);
}

// Chat toggle logic
const chatToggle = document.getElementById("chat-toggle");
const chatContainer = document.getElementById("chat-container");
const closeChat = document.getElementById("close-chat");

chatToggle.addEventListener("click", () => {
  chatContainer.style.display = "flex";
  chatToggle.style.display = "none";
});

closeChat.addEventListener("click", () => {
  chatContainer.style.display = "none";
  chatToggle.style.display = "block";
});
