# JARVIS Settings Interface - Frontend

This is the React frontend for the JARVIS Settings Interface, built with Vite, TypeScript, and Tailwind CSS.

## Development

To run the development server:

```bash
npm run dev
```

## Building

To build the production bundle:

```bash
npm run build
```

The built files will be output to the `dist` directory, which is served by the PyWebView backend.

## Technologies

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Hook Form** - Form management
- **Monaco Editor** - Code editor for prompts

## Project Structure

```
settings_ui/
├── src/
│   ├── components/     # React components
│   ├── App.tsx         # Main application component
│   └── main.tsx        # Entry point
├── public/             # Static assets
└── dist/               # Build output (generated)
```
