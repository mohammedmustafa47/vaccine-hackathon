document.addEventListener('DOMContentLoaded', function () {
    const sosToggle = document.getElementById('sosToggle');
    const sosButton = document.getElementById('sosButton');

    // Toggle Emergency Mode
    if (sosToggle) {
        sosToggle.addEventListener('change', function () {
            const formData = new FormData();
            formData.append("user_id", "{{ user.id }}"); // Ensure user ID is included
            formData.append("enabled", this.checked ? "true" : "false"); // Convert boolean to string

            fetch('/toggle-emergency', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    alert("✅ Emergency mode updated!");
                } else {
                    alert("⚠️ Error updating emergency mode!");
                }
            })
            .catch(error => console.error("❌ Error:", error));
        });
    }

    // SOS Alert Button
    if (sosButton) {
        sosButton.addEventListener("click", function () {
            if (!navigator.geolocation) {
                alert("❌ Geolocation is not supported by your browser.");
                return;
            }
        
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const payload = {
                        user_id: "{{ user.id }}",
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
        
                    fetch("/sos-alert", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === "SOS Sent") {
                            alert("🚨 SOS Alert Sent Successfully!");
                        } else {
                            alert("⚠️ Error: " + (data.error || "Could not send SOS alert"));
                        }
                    })
                    .catch(error => alert("❌ Error: Could not send SOS alert"));
                },
                (error) => {
                    alert("⚠️ Location access denied! Please enable location services.");
                }
            );
        });
        
    }
});
