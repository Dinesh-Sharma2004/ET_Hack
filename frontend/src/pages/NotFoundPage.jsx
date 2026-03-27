import { Link } from "react-router-dom";

import { Button } from "../components/ui/Button";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="max-w-xl rounded-[32px] border border-white/10 bg-white/6 p-8 text-center">
        <p className="text-xs uppercase tracking-[0.35em] text-slate-500">404</p>
        <h1 className="mt-3 font-display text-4xl">This page slipped off the news cycle.</h1>
        <p className="mt-4 text-sm leading-7 text-slate-300">
          Head back to the dashboard and continue exploring the newsroom.
        </p>
        <Link to="/" className="mt-6 inline-block">
          <Button>Return home</Button>
        </Link>
      </div>
    </div>
  );
}
