"use client";

export default function GradeBadge({ grade, score, size = "md" }: { grade: string; score?: number; size?: "sm" | "md" | "lg" }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className={`grade grade-${size} grade-${grade}`}>{grade}</span>
      {score !== undefined && <span className="text-caption text-gravel font-medium">{Math.round(score)}</span>}
    </div>
  );
}
