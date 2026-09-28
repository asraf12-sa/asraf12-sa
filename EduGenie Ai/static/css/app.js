// =========================================================
// DOM elements
// =========================================================

const task = document.getElementById("task");

const level = document.getElementById("level");

const input = document.getElementById("inputText");

const label = document.getElementById("inputLabel");

const weeks = document.getElementById("weeks");

const weeksLabel = document.getElementById("weeksLabel");

const button = document.getElementById("submitBtn");

const result = document.getElementById("result");

const status = document.getElementById("status");


// =========================================================
// Labels and placeholders
// =========================================================

const labels = {

    qa: [
        "Your Question",
        "Example: Which is the largest ocean?"
    ],

    explain: [
        "Topic to Explain",
        "Example: Pythagoras theorem"
    ],

    quiz: [
        "Passage or Topic",
        "Paste a passage or describe the topic for the quiz."
    ],

    summarize: [
        "Text to Summarize",
        "Paste the educational passage here."
    ],

    learn: [
        "Topic to Learn",
        "Example: SQL"
    ]

};


// =========================================================
// Update form
// =========================================================

function updateForm() {

    const selected = labels[task.value];

    label.textContent = selected[0];

    input.placeholder = selected[1];

    const learning =
        task.value === "learn";

    weeks.classList.toggle(
        "hidden",
        !learning
    );

    weeksLabel.classList.toggle(
        "hidden",
        !learning
    );

}


// =========================================================
// Change task
// =========================================================

task.addEventListener(
    "change",
    updateForm
);


// Initialize form

updateForm();


// =========================================================
// Escape HTML
// =========================================================

function escapeHtml(value) {

    return String(value).replace(
        /[&<>'"]/g,
        function (character) {

            const entities = {

                "&": "&amp;",

                "<": "&lt;",

                ">": "&gt;",

                "'": "&#39;",

                '"': "&quot;"

            };

            return entities[character];

        }
    );

}


// =========================================================
// Render normal text
// =========================================================

function renderText(
    title,
    text
) {

    return `
        <h2>${escapeHtml(title)}</h2>

        <pre>
${escapeHtml(text)}
        </pre>
    `;

}


// =========================================================
// Render quiz
// =========================================================

function renderQuiz(questions) {

    let html = "<h2>Quiz</h2>";

    questions.forEach(
        function (question, index) {

            html += `

                <article class="quiz-item">

                    <h3>
                        ${index + 1}.
                        ${escapeHtml(question.question)}
                    </h3>

            `;


            question.options.forEach(
                function (option) {

                    html += `

                        <div class="option">
                            ${escapeHtml(option)}
                        </div>

                    `;

                }
            );


            html += `

                    <p>
                        <strong>Answer:</strong>
                        ${escapeHtml(
                            question.correct_answer
                        )}
                    </p>

                    <p>
                        ${escapeHtml(
                            question.explanation || ""
                        )}
                    </p>

                </article>

            `;

        }
    );

    return html;
}


// =========================================================
// Get API endpoint
// =========================================================

function getEndpoint() {

    const endpoints = {

        qa: "/qa",

        explain: "/explain",

        quiz: "/quiz",

        summarize: "/summarize",

        learn: "/learn/recommendations"

    };

    return endpoints[task.value];

}


// =========================================================
// Build API request body
// =========================================================

function buildRequestBody(text) {

    if (task.value === "qa") {

        return {
            question: text
        };

    }


    if (task.value === "explain") {

        return {
            topic: text,
            level: level.value
        };

    }


    if (task.value === "quiz") {

        return {
            text: text,
            level: level.value
        };

    }


    if (task.value === "summarize") {

        return {
            text: text
        };

    }


    if (task.value === "learn") {

        return {
            topic: text,
            level: level.value,
            weeks: Number(weeks.value)
        };

    }

}


// =========================================================
// Render API response
// =========================================================

function renderResponse(data) {

    if (task.value === "qa") {

        return renderText(
            "Answer",
            data.answer
        );

    }


    if (task.value === "explain") {

        return renderText(
            "Explanation",
            data.explanation
        );

    }


    if (task.value === "quiz") {

        return renderQuiz(
            data.questions
        );

    }


    if (task.value === "summarize") {

        return renderText(
            "Summary",
            data.summary
        );

    }


    if (task.value === "learn") {

        return renderText(
            "Learning Path",
            data.plan
        );

    }


    return "<p>No result returned.</p>";

}


// =========================================================
// Submit
// =========================================================

button.addEventListener(
    "click",
    async function () {

        const text =
            input.value.trim();


        // Validate input

        if (!text) {

            status.textContent =
                "Please enter some content first.";

            return;

        }


        // Validate weeks

        if (
            task.value === "learn" &&
            (
                Number(weeks.value) < 1 ||
                Number(weeks.value) > 52
            )
        ) {

            status.textContent =
                "Learning duration must be between 1 and 52 weeks.";

            return;

        }


        // Disable button

        button.disabled = true;


        status.textContent =
            "EduGenie is thinking...";


        result.classList.add(
            "hidden"
        );


        try {

            const response =
                await fetch(
                    getEndpoint(),
                    {

                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(
                            buildRequestBody(text)
                        )

                    }
                );


            let data;


            try {

                data =
                    await response.json();

            } catch {

                throw new Error(
                    "Server returned an invalid response."
                );

            }


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Request failed."
                );

            }


            result.innerHTML =
                renderResponse(data);


            result.classList.remove(
                "hidden"
            );


            status.textContent =
                "Completed successfully.";

        }

        catch (error) {

            status.textContent =
                `Error: ${error.message}`;

        }

        finally {

            button.disabled = false;

        }

    }
);