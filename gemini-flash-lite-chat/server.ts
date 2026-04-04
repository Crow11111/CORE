import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import { fileURLToPath } from "url";
import session from "express-session";
import passport from "passport";
import { Strategy as GoogleStrategy } from "passport-google-oauth20";
import { google } from "googleapis";
import dotenv from "dotenv";
import fs from "fs";

dotenv.config({ path: ".env.local" });

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Configure Passport
passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID || "YOUR_CLIENT_ID",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "YOUR_CLIENT_SECRET",
      callbackURL: `${process.env.APP_URL}/auth/callback`,
    },
    (accessToken, refreshToken, profile, cb) => {
      const user = { ...profile, accessToken };
      return cb(null, user);
    },
  ),
);

passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj: any, done) => done(null, obj));

async function startServer() {
  const app = express();
  const PORT = 3005;

  app.use(express.json());
  app.set("trust proxy", 1);
  app.use(
    session({
      secret: "secret",
      resave: false,
      saveUninitialized: false,
      cookie: {
        secure: false, // Set to false for http://localhost
        sameSite: "lax",
        httpOnly: true,
      },
    }),
  );
  app.use(passport.initialize());
  app.use(passport.session());

  // API routes
  app.get("/api/user/profile", (req, res) => {
    if (!req.user) return res.status(401).json({ error: "Unauthorized" });
    res.json(req.user);
  });

  app.post("/api/auth/logout", (req, res) => {
    req.logout((err) => {
      if (err) {
        return res.status(500).json({ error: "Failed to logout" });
      }
      res.json({ success: true });
    });
  });

  app.get("/api/auth/url", (req, res) => {
    const scopes = [
      "profile",
      "email",
      "https://www.googleapis.com/auth/gmail.readonly",
      "https://www.googleapis.com/auth/drive.readonly",
      "https://www.googleapis.com/auth/calendar.readonly",
      "https://www.googleapis.com/auth/documents",
    ].join(" ");
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${process.env.GOOGLE_CLIENT_ID}&redirect_uri=${process.env.APP_URL}/auth/callback&response_type=code&scope=${encodeURIComponent(scopes)}&access_type=offline`;
    res.json({ url: authUrl });
  });

  app.get(
    "/auth/callback",
    passport.authenticate("google", { failureRedirect: "/login" }),
    (req, res) => {
      res.send(`
      <html>
        <head><title>Authentication Callback</title></head>
        <body style="background: #09090b; color: #fafafa; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0;">
          <script>
            console.log("OAuth callback triggered.");
            if (window.opener) {
              console.log("Found window.opener, sending OAUTH_AUTH_SUCCESS message...");
              try {
                window.opener.postMessage({ type: 'OAUTH_AUTH_SUCCESS' }, '*');
                console.log("Message sent. Closing window in 1 second...");
                setTimeout(() => {
                  window.close();
                }, 1000);
              } catch (e) {
                console.error("Error sending postMessage:", e);
                document.body.innerHTML += '<p style="color: #ef4444;">Fehler beim Senden der Nachricht an das Hauptfenster.</p>';
              }
            } else {
              console.error("window.opener not found. Redirecting to home...");
              window.location.href = '/';
            }
          </script>
          <div style="text-align: center;">
            <p>Authentication successful.</p>
            <p style="font-size: 0.8rem; color: #a1a1aa;">This window should close automatically.</p>
          </div>
        </body>
      </html>
    `);
    },
  );

  app.get("/api/drive/files", async (req, res) => {
    try {
      if (!req.user) return res.status(401).json({ error: "Unauthorized" });
      const accessToken = (req.user as any).accessToken;
      const auth = new google.auth.OAuth2();
      auth.setCredentials({ access_token: accessToken });
      const drive = google.drive({ version: "v3", auth });
      const files = await drive.files.list({
        pageSize: 10,
        fields: "files(id, name, webViewLink)",
      });
      res.json({ files: files.data.files });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.get("/api/calendar/events", async (req, res) => {
    try {
      if (!req.user) return res.status(401).json({ error: "Unauthorized" });
      const accessToken = (req.user as any).accessToken;
      const auth = new google.auth.OAuth2();
      auth.setCredentials({ access_token: accessToken });
      const calendar = google.calendar({ version: "v3", auth });
      const events = await calendar.events.list({
        calendarId: "primary",
        timeMin: new Date().toISOString(),
        maxResults: 10,
        singleEvents: true,
        orderBy: "startTime",
      });
      res.json({ events: events.data.items });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/docs/create", async (req, res) => {
    try {
      if (!req.user) return res.status(401).json({ error: "Unauthorized" });
      const accessToken = (req.user as any).accessToken;
      const auth = new google.auth.OAuth2();
      auth.setCredentials({ access_token: accessToken });
      const docs = google.docs({ version: "v1", auth });
      const doc = await docs.documents.create({
        requestBody: { title: req.body.title },
      });
      res.json({ documentId: doc.data.documentId, title: doc.data.title });
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  });

  app.post("/api/github/dispatch", async (req, res) => {
    try {
      if (!req.user) return res.status(401).json({ error: "Unauthorized" });
      const { event_type, client_payload } = req.body;
      const githubPat = process.env.GITHUB_PAT?.trim();
      if (!githubPat) {
        return res.status(503).json({
          error: "GITHUB_PAT is not configured (set in environment, never commit).",
        });
      }

      const response = await fetch(
        "https://api.github.com/repos/Crow11111/MTHO_CORE/dispatches",
        {
          method: "POST",
          headers: {
            Accept: "application/vnd.github+json",
            Authorization: `Bearer ${githubPat}`,
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "Gemini-Live-App",
          },
          body: JSON.stringify({
            event_type: event_type || "gemini_update",
            client_payload:
              typeof client_payload === "string"
                ? JSON.parse(client_payload)
                : client_payload || {},
          }),
        },
      );

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`GitHub API error: ${response.status} - ${errText}`);
      }

      res.json({
        success: true,
        message: "Successfully dispatched to GitHub webhook.",
      });
    } catch (error: any) {
      console.error("GitHub Webhook Error:", error);
      res.status(500).json({ error: error.message });
    }
  });

  // Proxy to OMEGA Backend (:8000)
  app.post("/api/omega/task", async (req, res) => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req.body),
      });
      const data = await response.json();
      res.status(response.status).json(data);
    } catch (error: any) {
      console.error("OMEGA Backend Proxy Error:", error.message);
      res.status(500).json({ error: error.message });
    }
  });

  // Cursor Input Injection Bridge
  app.post("/api/cursor/inject", async (req, res) => {
    try {
      const { content } = req.body;
      if (!content)
        return res.status(400).json({ error: "No content provided" });

      const injectionPath = "/OMEGA_CORE/data/cursor_injection.txt";
      const dir = path.dirname(injectionPath);

      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      fs.appendFileSync(injectionPath, content + "\n", "utf8");
      res.json({
        success: true,
        message: "Content injected into cursor_injection.txt",
      });
    } catch (error: any) {
      console.error("Cursor Injection Error:", error);
      res.status(500).json({ error: error.message });
    }
  });

  // Local File Write Bridge
  app.post("/api/system/write", async (req, res) => {
    try {
      const { text, path: targetPath } = req.body;
      if (!text || !targetPath)
        return res.status(400).json({ error: "No text or path provided" });

      // Clean path and prevent directory traversal
      const safePath = path
        .normalize(targetPath)
        .replace(/^(\.\.(\/|\\|$))+/, "");
      const fullPath = path.isAbsolute(safePath)
        ? safePath
        : path.join("/OMEGA_CORE", safePath);

      const dir = path.dirname(fullPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      fs.writeFileSync(fullPath, text, "utf8");
      res.json({ success: true, message: `Successfully wrote to ${fullPath}` });
    } catch (error: any) {
      console.error("Local File Write Error:", error);
      res.status(500).json({ error: error.message });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(__dirname, "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
