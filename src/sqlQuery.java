import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.text.ParseException;
import java.util.Scanner;

public class sqlQuery {
    public static void main(String[] args) throws ParseException, InterruptedException {
        getSql();
    }
    static HttpClient httpClient = HttpClient.newHttpClient();
    static String apiUrl = "https://api.openai.com/v1/completions";

    // Set your OpenAI API key
    static String apiKey = "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";
    static String columns = "Year, Round, Pick, Team, Position, Player, School ,Type ,State ,Signed, Salary and Report";
    public static void getSql() throws ParseException, InterruptedException {
        Scanner myObj = new Scanner(System.in);
        while(true) {
            System.out.println("Please enter what you would like to search for");
            String prompt = "write an sql script on the table Players to select ";
            prompt = prompt + myObj.nextLine() + " the columns are " + columns;
            prompt = prompt + " the options for position are - P, C, 1B, 2B, 3B, SS, OF, P, LHP, SHP";
            apiCall(prompt);
        }
    }
    public static void apiCall(String prompt) throws ParseException, InterruptedException {
        try {
            // Set up your OpenAI API credentials
            String apiKey = "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";

            // Set up the API endpoint URL
            String url = "https://api.openai.com/v1/engines/davinci-codex/completions";

            // Set up the request headers
                String authorizationHeader = "Bearer " + apiKey;
            String contentTypeHeader = "application/json";

            // Set up the request payload
            int maxTokens = 200;
            int n = 1;
            String stop = null;

            // Construct the request payload as a JSON string
            String jsonInputString = "{" +
                    "\"prompt\": \"" + prompt + "\", " +
                    "\"max_tokens\": " + maxTokens + ", " +
                    "\"n\": " + n + ", " +
                    "\"stop\": " + stop + ", " +
                    "\"temperature\": 1, " +
                    "\"top_p\": 1, " +
                    "\"frequency_penalty\": 0, " +
                    "\"presence_penalty\": 0, " +
                    "\"model\": \"text-davinci-003\", " +
                    "\"echo\": true" +
                    "}";

            // Create the HTTP connection
            URL apiUrl = new URL(url);
            HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Authorization", authorizationHeader);
            connection.setRequestProperty("Content-Type", contentTypeHeader);
            connection.setDoOutput(true);

            // Send the request payload
            DataOutputStream outputStream = new DataOutputStream(connection.getOutputStream());
            outputStream.write(jsonInputString.getBytes(StandardCharsets.UTF_8));
            outputStream.flush();
            outputStream.close();

            // Read and display the response
            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            String line;
            StringBuilder response = new StringBuilder();
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();

            System.out.println(response.toString());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}