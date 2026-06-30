import Card from "./Card";

interface Props {
  title: string;
  value: string;
}

export default function StatCard({
  title,
  value,
}: Props) {
  return (
    <Card className="p-6">
      <p className="text-sm text-slate-500">
        {title}
      </p>

      <h3 className="mt-3 text-3xl font-bold">
        {value}
      </h3>
    </Card>
  );
}