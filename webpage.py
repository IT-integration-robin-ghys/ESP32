html = """
  <!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Terrarium</title>
  </head>

  <body>
    <div id="data">
      <h1>Live data</h1>

      <p>Temperature: <span id="live_temperature">-</span></p>
      <p>Humidity: <span id="live_humidity">-</span></p>
      <p>Pressure: <span id="pressure">-</span></p>
    </div>

    <div id="connect_wifi">
      <h1>Connect to WiFi</h1>

      <form id="wifiForm">
        <label for="ssid">WiFi SSID</label><br />
        <input type="text" id="ssid" name="ssid" /><br />

        <label for="password">Password</label><br />
        <input type="password" id="password" name="password" /><br />

        <button type="submit">Connect</button>
      </form>
    </div>

    <div id="connect_email">
      <h1>Connect device to account</h1>

      <form id="emailForm">
        <label for="terrarium_name">Terrarium name</label><br />
        <input type="text" id="terrarium_name" name="terrarium_name" /><br />

        <label for="email">Email address</label><br />
        <input type="email" id="email" name="email" /><br />

        <button type="submit">Connect device</button><br />
      </form>
    </div>

    <div id="settings">
      <h1>Terrarium settings</h1>

      <form id="settingsForm">
        <h2>Day settings</h2>

        <label for="day_start_time">Start time</label><br />
        <input type="number" id="day_start_time" min="0" max="23" /><br />

        <label for="day_temp">Target temperature</label><br />
        <input type="number" id="day_temp" step="0.1" /><br />

        <label for="day_temp_margin">Temperature margin</label><br />
        <input type="number" id="day_temp_margin" step="0.1" /><br />

        <label for="day_temp_too_high_margin">
          Temperature too high margin </label
        ><br />
        <input type="number" id="day_temp_too_high_margin" step="0.1" /><br />

        <label for="day_humidity">Target humidity</label><br />
        <input type="number" id="day_humidity" step="0.1" /><br />

        <label for="day_humidity_margin">Humidity margin</label><br />
        <input type="number" id="day_humidity_margin" step="0.1" /><br />

        <h2>Night settings</h2>

        <label for="night_start_time">Start time</label><br />
        <input type="number" id="night_start_time" min="0" max="23" /><br />

        <label for="night_temp">Target temperature</label><br />
        <input type="number" id="night_temp" step="0.1" /><br />

        <label for="night_temp_margin">Temperature margin</label><br />
        <input type="number" id="night_temp_margin" step="0.1" /><br />

        <label for="night_temp_too_high_margin">
          Temperature too high margin </label
        ><br />
        <input type="number" id="night_temp_too_high_margin" step="0.1" /><br />

        <label for="night_humidity">Target humidity</label><br />
        <input type="number" id="night_humidity" step="0.1" /><br />

        <label for="night_humidity_margin">Humidity margin</label><br />
        <input type="number" id="night_humidity_margin" step="0.1" /><br />

        <h2>Feeder settings</h2>

        <p>Feeding days:</p>

        <label>
          <input type="checkbox" name="feeding_day" value="0" />
          Monday </label
        ><br />

        <label>
          <input type="checkbox" name="feeding_day" value="1" />
          Tuesday </label
        ><br />

        <label>
          <input type="checkbox" name="feeding_day" value="2" />
          Wednesday </label
        ><br />

        <label>
          <input type="checkbox" name="feeding_day" value="3" />
          Thursday </label
        ><br />

        <label>
          <input type="checkbox" name="feeding_day" value="4" />
          Friday </label
        ><br />

        <label>
          <input type="checkbox" name="feeding_day" value="5" />
          Saturday </label
        ><br />

        <label>
          <input type="checkbox" name="feeding_day" value="6" />
          Sunday </label
        ><br /><br />

        <label for="time_first_portion"> First portion time </label><br />

        <input type="number" id="time_first_portion" min="0" max="23" /><br />

        <label for="time_second_portion"> Second portion time </label><br />

        <input
          type="number"
          id="time_second_portion"
          min="0"
          max="23"
        /><br /><br />

        <button type="submit">Save settings</button>
      </form>
    </div>

    <script>
      const updateData = async () => {
        const response = await fetch("/data");
        const data = await response.json();

        document.getElementById("live_temperature").textContent =
          data.temperature;

        document.getElementById("live_humidity").textContent = data.humidity;

        document.getElementById("pressure").textContent = data.pressure;
      };

      const loadSettings = async () => {
        try {
          const response = await fetch("/settings");
          const settings = await response.json();

          const day = settings.day;
          const night = settings.night;
          const feeder = settings.feeder;

          document.getElementById("day_start_time").value = day.start_time;

          document.getElementById("day_temp").value = day.temp;

          document.getElementById("day_temp_margin").value = day.temp_margin;

          document.getElementById("day_temp_too_high_margin").value =
            day.temp_too_high_margin;

          document.getElementById("day_humidity").value = day.humidity;

          document.getElementById("day_humidity_margin").value =
            day.humidity_margin;

          document.getElementById("night_start_time").value = night.start_time;

          document.getElementById("night_temp").value = night.temp;

          document.getElementById("night_temp_margin").value =
            night.temp_margin;

          document.getElementById("night_temp_too_high_margin").value =
            night.temp_too_high_margin;

          document.getElementById("night_humidity").value = night.humidity;

          document.getElementById("night_humidity_margin").value =
            night.humidity_margin;

          document.getElementById("time_first_portion").value =
            feeder.time_first_portion;

          document.getElementById("time_second_portion").value =
            feeder.time_second_portion;

          const feedingDays = document.querySelectorAll(
            'input[name="feeding_day"]',
          );

          feedingDays.forEach((checkbox) => {
            checkbox.checked = feeder.days.includes(Number(checkbox.value));
          });
        } catch (error) {
          console.log("Could not load settings:", error);
        }
      };

      const settingsForm = document.getElementById("settingsForm");

      settingsForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const feedingDays = [];

        document
          .querySelectorAll('input[name="feeding_day"]:checked')
          .forEach((checkbox) => {
            feedingDays.push(Number(checkbox.value));
          });

        const settings = {
          day: {
            start_time: Number(document.getElementById("day_start_time").value),

            temp: Number(document.getElementById("day_temp").value),

            temp_margin: Number(
              document.getElementById("day_temp_margin").value,
            ),

            temp_too_high_margin: Number(
              document.getElementById("day_temp_too_high_margin").value,
            ),

            humidity: Number(document.getElementById("day_humidity").value),

            humidity_margin: Number(
              document.getElementById("day_humidity_margin").value,
            ),
          },

          night: {
            start_time: Number(
              document.getElementById("night_start_time").value,
            ),

            temp: Number(document.getElementById("night_temp").value),

            temp_margin: Number(
              document.getElementById("night_temp_margin").value,
            ),

            temp_too_high_margin: Number(
              document.getElementById("night_temp_too_high_margin").value,
            ),

            humidity: Number(document.getElementById("night_humidity").value),

            humidity_margin: Number(
              document.getElementById("night_humidity_margin").value,
            ),
          },

          feeder: {
            days: feedingDays,

            time_first_portion: Number(
              document.getElementById("time_first_portion").value,
            ),

            time_second_portion: Number(
              document.getElementById("time_second_portion").value,
            ),
          },
        };

        try {
          const response = await fetch("/settings", {
            method: "POST",

            headers: {
              "Content-Type": "application/json",
            },

            body: JSON.stringify(settings),
          });

          const data = await response.json();

          alert(data.message);
        } catch (error) {
          console.log("Could not save settings:", error);

          alert("Could not save settings");
        }
      });

      const wifiForm = document.getElementById("wifiForm");

      wifiForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const ssid = document.getElementById("ssid").value;
        const password = document.getElementById("password").value;

        const response = await fetch("/wifi", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ssid: ssid,
            password: password,
          }),
        });
        const data = await response.json();

        data.success
          ? alert(
              `Connection successfull, you can connect through the new ip: ${data.ip}`,
            )
          : alert(`Connecting to wifi failed`);
      });

      const emailForm = document.getElementById("emailForm");

      emailForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const terrarium_name = document.getElementById("terrarium_name").value;

        const response = await fetch("/email", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            terrarium_name: terrarium_name,
          }),
        });

        const data = await response.json();

        alert(data.message);
      });

      updateData();
      loadSettings();
      setInterval(updateData, 10000);
    </script>
  </body>
</html>

    """