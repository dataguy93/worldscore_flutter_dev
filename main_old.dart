void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  runApp(const WorldScoreAIApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WorldScore AI',
      home: Scaffold(
        appBar: AppBar(title: const Text('Firebase Ready')),
        body: const Center(
          child: Text('Firebase initialized successfully'),
        ),
      ),
    );
  }
}
