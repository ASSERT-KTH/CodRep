declare warning : @args(MyAnnotation) : "@args is not allowed in declares...";

public aspect DeclareEoW {
	
	declare warning : @args(@MyAnnotation) : "@args is not allowed in declares...";
	
}
 No newline at end of file