import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "../adr-compliance-checker.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
