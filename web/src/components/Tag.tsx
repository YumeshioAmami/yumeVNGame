export default function Tag({
  children,
  tone = "default",
}: {
  children: React.ReactNode;
  tone?: "default" | "accent" | "warm" | "danger";
}) {
  return <span className={`tag tag-${tone}`}>{children}</span>;
}

