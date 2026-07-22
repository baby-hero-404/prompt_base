# Spatial Computing (XR) & Voice UI

Mobile app design is no longer just flat screens. The 2026 standard includes conversational interfaces and spatial computing.

## Spatial Computing (visionOS / XR)

When designing for headsets/XR environments:
- **Z-Axis matters:** Elements can be pushed forward or backward in 3D space. Push interactive elements closer to the user.
- **Glass Materials:** Use system-provided glassmorphism materials (e.g., in visionOS) rather than opaque colors so users maintain situational awareness of their room.
- **Eye Tracking & Pinch:** UI elements must be large enough to be easily targeted by eye tracking. Hover states are triggered by looking. The "click" is a finger pinch.
- **Shared Space vs Full Space:** Apps start in a windowed Shared Space. Only go to Full Space (VR mode) when total immersion is required.

## Conversational & Voice UI

- **Multimodal by default:** A user might tap a button, or they might speak a command. The UI should instantly reflect voice input.
- **Streaming transcripts:** When a user is speaking, show the transcribed text in real-time.
- **VUI (Voice User Interface) Feedback:** Provide subtle audio cues or haptic feedback when the microphone opens or closes.
- **LLM Latency UI:** When waiting for an AI response, use skeleton loaders, pulsing avatars, or generative "thinking" animations rather than generic spinners.
