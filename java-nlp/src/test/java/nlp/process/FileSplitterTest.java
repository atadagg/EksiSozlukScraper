package nlp.process;

import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.*;
import java.io.*;
import java.util.List;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import Corpus.Sentence;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class FileSplitterTest {
    @TempDir
    Path tempDir;
    
    private Path testInputFile;
    private Path testOutputFile;
    private Path testAllSentencesFile;
    private FileSplitter fileSplitter;
    private Gson gson;

    @BeforeEach
    void init() throws IOException {
        testInputFile = tempDir.resolve("test_input.jsonl");
        testOutputFile = tempDir.resolve("test_output.txt");
        testAllSentencesFile = tempDir.resolve("test_all_sentences.txt");
        gson = new Gson();
        fileSplitter = new FileSplitter();
    }

    @Test
    void testProcessEmptyFile() throws IOException {
        // Create empty input file
        Files.createFile(testInputFile);
        
        // Process the file
        fileSplitter.processFile(testInputFile.toString(), testOutputFile.toString(), testAllSentencesFile.toString());
        
        // Verify output files are created but empty
        Assertions.assertTrue(Files.exists(testOutputFile));
        Assertions.assertTrue(Files.exists(testAllSentencesFile));
        Assertions.assertEquals("", Files.readString(testOutputFile));
        Assertions.assertEquals("", Files.readString(testAllSentencesFile));
    }

    @Test
    void testProcessSingleEntry() throws IOException {
        // Create test input with one entry
        JsonObject entry = new JsonObject();
        entry.addProperty("id", "1");
        entry.addProperty("content", "Bu bir test cümlesi. İkinci cümle.");
        entry.addProperty("timestamp", "2024-03-20 12:00:00");
        
        Files.writeString(testInputFile, gson.toJson(entry) + "\n");
        
        // Process the file
        fileSplitter.processFile(testInputFile.toString(), testOutputFile.toString(), testAllSentencesFile.toString());
        
        // Verify output
        String output = Files.readString(testOutputFile);
        String allSentences = Files.readString(testAllSentencesFile);
        
        Assertions.assertTrue(output.contains("Bu bir test cümlesi"));
        Assertions.assertTrue(output.contains("İkinci cümle"));
        Assertions.assertEquals(output, allSentences);
    }

    @Test
    void testProcessMultipleEntries() throws IOException {
        // Create test input with multiple entries
        JsonObject entry1 = new JsonObject();
        entry1.addProperty("id", "1");
        entry1.addProperty("content", "İlk entry. İkinci cümle.");
        entry1.addProperty("timestamp", "2024-03-20 12:00:00");

        JsonObject entry2 = new JsonObject();
        entry2.addProperty("id", "2");
        entry2.addProperty("content", "İkinci entry. Başka bir cümle.");
        entry2.addProperty("timestamp", "2024-03-20 12:01:00");

        Files.writeString(testInputFile, 
            gson.toJson(entry1) + "\n" + 
            gson.toJson(entry2) + "\n");
        
        // Process the file
        fileSplitter.processFile(testInputFile.toString(), testOutputFile.toString(), testAllSentencesFile.toString());
        
        // Verify output
        String output = Files.readString(testOutputFile);
        String allSentences = Files.readString(testAllSentencesFile);
        
        Assertions.assertTrue(output.contains("İlk entry"));
        Assertions.assertTrue(output.contains("İkinci cümle"));
        Assertions.assertTrue(output.contains("İkinci entry"));
        Assertions.assertTrue(output.contains("Başka bir cümle"));
        Assertions.assertEquals(output, allSentences);
    }

    @Test
    void testAppendToAllSentences() throws IOException {
        // First batch
        JsonObject entry1 = new JsonObject();
        entry1.addProperty("id", "1");
        entry1.addProperty("content", "İlk batch. İlk cümle.");
        entry1.addProperty("timestamp", "2024-03-20 12:00:00");
        
        Files.writeString(testInputFile, gson.toJson(entry1) + "\n");
        fileSplitter.processFile(testInputFile.toString(), testOutputFile.toString(), testAllSentencesFile.toString());
        
        // Second batch
        JsonObject entry2 = new JsonObject();
        entry2.addProperty("id", "2");
        entry2.addProperty("content", "İkinci batch. İkinci cümle.");
        entry2.addProperty("timestamp", "2024-03-20 12:01:00");
        
        Files.writeString(testInputFile, gson.toJson(entry2) + "\n");
        fileSplitter.processFile(testInputFile.toString(), testOutputFile.toString(), testAllSentencesFile.toString());
        
        // Verify all_sentences.txt contains both batches
        String allSentences = Files.readString(testAllSentencesFile);
        Assertions.assertTrue(allSentences.contains("İlk batch"));
        Assertions.assertTrue(allSentences.contains("İlk cümle"));
        Assertions.assertTrue(allSentences.contains("İkinci batch"));
        Assertions.assertTrue(allSentences.contains("İkinci cümle"));
    }

    @Test
    void testInvalidJson() throws IOException {
        // Create test input with invalid JSON
        Files.writeString(testInputFile, "invalid json\n");
        
        // Process the file
        fileSplitter.processFile(testInputFile.toString(), testOutputFile.toString(), testAllSentencesFile.toString());
        
        // Verify output files are created but empty
        Assertions.assertTrue(Files.exists(testOutputFile));
        Assertions.assertTrue(Files.exists(testAllSentencesFile));
        Assertions.assertEquals("", Files.readString(testOutputFile));
        Assertions.assertEquals("", Files.readString(testAllSentencesFile));
    }
} 