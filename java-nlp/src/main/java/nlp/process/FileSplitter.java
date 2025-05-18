package nlp.process;
import Corpus.TurkishSplitter;
import Corpus.Sentence;
import java.nio.file.*;
import java.io.IOException;
import java.util.ArrayList;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.BufferedReader;
import java.io.FileReader;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class FileSplitter {
    private static final String filePath = "../python-scraper/data_diff.jsonl";
    private static final String outputPath = "src/main/resources/new_sentences.txt";
    private static final String allSentencesPath = "src/main/resources/all_sentences.txt";
    private static final Gson gson = new Gson();
    private static final TurkishSplitter splitter = new TurkishSplitter();

    public static void main(String[] args) {
        try {
            Path file = Paths.get(filePath);
            long lastModified = 0;

            System.out.println("Watching for changes in: " + filePath);

            while (true) {
                if (Files.exists(file)) {
                    long currentModified = Files.getLastModifiedTime(file).toMillis();
                    if (currentModified > lastModified) {
                        processFile();
                        lastModified = currentModified;
                    }
                }
                Thread.sleep(30000); // Check every 30 seconds
            }
        } catch (IOException | InterruptedException e) {
            System.err.println("Error watching file: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void processFile() {
        try {
            if (!Files.exists(Paths.get(filePath))) {
                System.err.println("Error: File does not exist at path: " + filePath);
                return;
            }

            StringBuilder results = new StringBuilder();
            ArrayList<Sentence> allSentences = new ArrayList<>();

            try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.trim().isEmpty()) continue;
                    
                    JsonObject entry = gson.fromJson(line, JsonObject.class);
                    String content = entry.get("content").getAsString();
                    
                    if (!content.trim().isEmpty()) {
                        var sentences = splitter.split(content);
                        allSentences.addAll(sentences);
                    }
                }
            }

            // Write to the current results file
            for (Sentence sentence : allSentences) {
                results.append(sentence).append("\n");
            }
            Files.writeString(Paths.get(outputPath), results.toString());

            // Append to all_sentences.txt
            try {
                Files.write(Paths.get(allSentencesPath), 
                          results.toString().getBytes(), 
                          StandardOpenOption.CREATE, 
                          StandardOpenOption.APPEND);
            } catch (IOException e) {
                System.err.println("Error appending to all_sentences.txt: " + e.getMessage());
            }

            System.out.println("[" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")) + 
                             "] Updated results in: " + outputPath + " and appended to " + allSentencesPath);

        } catch (IOException e) {
            System.err.println("Error processing file: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("Error processing text: " + e.getMessage());
            e.printStackTrace();
        }
    }
}