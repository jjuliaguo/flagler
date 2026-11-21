interface Appointment {
  id: string;
  providerId: string;
  start: Date;
  durationMin: number;
}

/**
 * Returns pairs of appointment IDs that overlap for the same provider,
 * so the scheduling team can reach out and rebook one of them.
 */
function findConflicts(appts: Appointment[]): Array<[string, string]> {
  const byProvider: Record<string, Appointment[]> = {};
  for (const a of appts) {
    (byProvider[a.providerId] ||= []).push(a);
  }

  const conflicts: Array<[string, string]> = [];
  for (const providerId in byProvider) {
    const list = byProvider[providerId].sort((a, b) =>
      a.start > b.start ? 1 : -1
    );

    for (let i = 0; i < list.length - 1; i++) {
      const cur = list[i];
      const next = list[i + 1];
      const curEnd = new Date(cur.start.getTime() + cur.durationMin * 60);

      if (curEnd > next.start) {
        conflicts.push([cur.id, next.id]);
      }
    }
  }
  return conflicts;
}
