export interface Challenge {
  id?: string;

  title: string;
  description: string;

  category: string;
  challenge_type: string;

  difficulty: string;

  points: number;
  target_value: number;
  duration_days: number;

  status?: string;
  ai_generated?: boolean;

  created_by?: string;
  approved_by?: string | null;
}

export interface ChallengeParticipant {
  id: string;

  challenge_id: string;

  progress: number;

  completed: boolean;

  points_awarded: number;
}