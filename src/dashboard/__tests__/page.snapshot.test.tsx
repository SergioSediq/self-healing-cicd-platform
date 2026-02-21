import { render } from "@testing-library/react";
import Dashboard from "../app/page";

jest.mock("global.fetch", () =>
  jest.fn(() =>
    Promise.resolve({
      json: () =>
        Promise.resolve({
          last_run_id: "snap-1",
          status: "healed",
          logs: "test log",
          timestamp: Date.now() / 1000,
          analysis: {
            root_cause: "Missing env",
            suggested_fix: "Add FIX_APPLIED",
            confidence_score: 0.9,
          },
        }),
    })
  )
);

describe("Dashboard snapshot", () => {
  it("matches snapshot when loaded", async () => {
    const { container } = render(<Dashboard />);
    await new Promise((r) => setTimeout(r, 100));
    expect(container).toMatchSnapshot();
  });
});
