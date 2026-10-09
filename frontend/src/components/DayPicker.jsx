import { DAYS, todayIndex } from "../api";

export default function DayPicker({ value, onChange, allowAll = false }) {
  const today = todayIndex();
  return (
    <div className="day-picker">
      {allowAll && (
        <button className={value === null ? "active" : ""} onClick={() => onChange(null)}>
          All
        </button>
      )}
      {DAYS.map((d, i) => (
        <button
          key={d}
          className={`${value === i ? "active" : ""} ${i >= 5 ? "weekend" : ""}`}
          onClick={() => onChange(i)}
          title={i === today ? "Today" : d}
        >
          {d.slice(0, 3)}
          {i === today && <span className="dot" />}
        </button>
      ))}
    </div>
  );
}
