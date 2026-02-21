import { render, screen } from "@testing-library/react";
import Dashboard from "../app/page";

const mockData = {
  last_run_id: "test-123",
  status: "idle",
  logs: "",
  timestamp: Date.now() / 1000,
  analysis: { root_cause: null, suggested_fix: null, confidence_score: 0 },
};

beforeEach(() => {
  (global.fetch as jest.Mock) = jest.fn(() =>
    Promise.resolve({ json: () => Promise.resolve(mockData) })
  );
});

describe("Dashboard", () => {
  it("renders AI OPS HEALER heading after load", async () => {
    render(<Dashboard />);
    expect(await screen.findByText(/AI OPS/i)).toBeInTheDocument();
  });
});
