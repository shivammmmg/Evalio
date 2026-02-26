export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export type CourseAssessment = {
  name: string;
  weight: number;
  raw_score?: number | null;
  total_score?: number | null;
};

export type Course = {
  course_id: string;
  name: string;
  term?: string | null;
  assessments: CourseAssessment[];
};

export type CreateCourseResponse = {
  message: string;
  total_weight: number;
  course_id: string;
  course: Omit<Course, "course_id">;
};

export type YorkEquivalent = {
  letter: string;
  grade_point: number;
  description: string;
};

export type TargetCheckResponse = {
  target: number;
  current_standing: number;
  maximum_possible: number;
  feasible: boolean;
  explanation: string;
  york_equivalent: YorkEquivalent;
  required_points: number;
  required_average: number;
  required_average_display: string;
  required_fraction_display: string;
  classification: string;
};

export type UpdateCourseGradesResponse = {
  message: string;
  course_id: string;
  course_index?: number;
  current_standing: number;
  assessments: Array<{
    name: string;
    weight: number;
    raw_score: number | null;
    total_score: number | null;
  }>;
};

export type WhatIfResponse = {
  course_name: string;
  assessment_name: string;
  assessment_weight: number;
  hypothetical_score: number;
  hypothetical_contribution: number;
  current_standing: number;
  projected_grade: number;
  remaining_potential: number;
  maximum_possible: number;
  york_equivalent: YorkEquivalent;
  explanation: string;
};

export type MinimumRequiredResponse = {
  course_name: string;
  assessment_name: string;
  assessment_weight: number;
  minimum_required: number;
  is_achievable: boolean;
  current_standing: number;
  other_remaining_assumed_max: number;
  target: number;
  explanation: string;
};

export type ApiError = Error & {
  response?: {
    data?: unknown;
  };
};

function getDetail(body: unknown): string | null {
  if (!body || typeof body !== "object") return null;
  const detail = (body as { detail?: unknown }).detail;
  return typeof detail === "string" && detail.trim() ? detail : null;
}

async function request(path: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => undefined);
    const message = getDetail(body) ?? `Request failed: ${response.status}`;
    const error = new Error(message) as ApiError;
    error.response = { data: body };
    throw error;
  }

  return response.json();
}

export function listCourses() {
  return request("/courses/") as Promise<Course[]>;
}

export function createCourse(payload: {
  name: string;
  term?: string | null;
  assessments: Array<{
    name: string;
    weight: number;
    raw_score?: number | null;
    total_score?: number | null;
  }>;
}) {
  return request("/courses/", {
    method: "POST",
    body: JSON.stringify(payload),
  }) as Promise<CreateCourseResponse>;
}

export function updateCourseWeights(
  courseId: string,
  payload: { assessments: Array<{ name: string; weight: number }> }
) {
  return request(`/courses/${courseId}/weights`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function updateCourseGrades(
  courseId: string,
  payload: {
    assessments: Array<{
      name: string;
      raw_score: number | null;
      total_score: number | null;
    }>;
  }
) {
  return request(`/courses/${courseId}/grades`, {
    method: "PUT",
    body: JSON.stringify(payload),
  }) as Promise<UpdateCourseGradesResponse>;
}

export function checkTarget(courseId: string, payload: { target: number }) {
  return request(`/courses/${courseId}/target`, {
    method: "POST",
    body: JSON.stringify(payload),
  }) as Promise<TargetCheckResponse>;
}

export function runWhatIf(
  courseId: string,
  payload: { assessment_name: string; hypothetical_score: number }
) {
  return request(`/courses/${courseId}/whatif`, {
    method: "POST",
    body: JSON.stringify(payload),
  }) as Promise<WhatIfResponse>;
}

export function getMinimumRequired(
  courseId: string,
  payload: { target: number; assessment_name: string }
) {
  return request(`/courses/${courseId}/minimum-required`, {
    method: "POST",
    body: JSON.stringify(payload),
  }) as Promise<MinimumRequiredResponse>;
}
