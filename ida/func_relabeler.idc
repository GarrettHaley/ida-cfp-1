/*
 * Defines the JSON-based function relaber.
 *
 * Manages and interacts with structures and the bundle.json file to create
 * a mapping between what functions are currently displayed as, and what they
 * should be.
 */

#include <idc.idc>

/*
 * List
 *
 * Manages all of the bundle items.
 *
 * Class List exists largely as the high level manager for interacting with both
 * the `bundle.json` and the ELF binary itself.
 */
class List
{
  List()
  {
		this.__count = 0;
  }

  size()
  {
		return this.__count;
  }

  add(e)
  {
    this[this.__count++] = e;
  }
}

/*
 * BundleItem
 *
 * Contains the string mapping between the `bundle.json` and the IDA strings.
 *
 * Managing everything in one object is by far and away the simplest
 * implementation, especially considering IDC does not support most of the
 * common data structures.
 */
class BundleItem
{
   BundleItem(string_from_bundle, func_from_bundle, str_addr_from_ida, str_xref_from_ida) 
   {
      this.string_from_bundle = string_from_bundle;     
	  
      this.func_from_bundle = func_from_bundle;    
	  
      this.str_addr_from_ida = str_addr_from_ida;
	  
      this.str_xref_from_ida = str_xref_from_ida;  	  
   }
}

/*
 * Get IDA Bundle
 *
 * Populates an `IDA Bundle`, which contains mappings of string: function name.
 *
 * Utilizes the effective address system available through the included idc.idc
 * API to search the ELF binary for candidate strings. In the event one is
 * located, it is added to the instance of the List class.
 */
static get_ida_bundle()
{
	auto string_name, function_name, xref_first, xref_second;
	auto ida_bundle = List();

	// Get the first effective address in the iterable IDA-DB. BeginEA does not
	// exist in the defined `idc.idc` API but instead is exposed via the idc.py
	// API. Specifically returns a `long` of the linear address of program
	// entry point
	auto ea = BeginEA(); 

	// `MaxEA` is much like `BeginEA` in that it is not available via idc.idc.
	// Returns the highest address used in the target file
	auto max_ea = MaxEA();
  
	while(ea < max_ea && ea != BADADDR)
	{
		// Get the next defined item (instruction or data) in the program, or
		// returns BADADDR (no more defined items). `ea` is the linear address
		// to start the search from and `max_ea` is the address to stop the
		// search at (exclusive)
		ea = next_head(ea, max_ea);
		
		// Get the string type from an effective address/linear address. Returns
		// one of the STRTYPE_* constants like the following: STRTYPE_C,
		// STRTYPE_C_16, STRTYPE_LEN4_16, etc. STRTYPE_C is a C-style null
		// terminated string
		if (get_str_type(ea) == STRTYPE_C)
		{
			// Convert address to `function name + offset` string with `ea` being
			// the address to convert. Returns a string formed as
			// `function name + offset` if the address belongs to a defined function
			// or `0` if the address is unassociated. The `function name + offset`
			// corresponds to the name of the function and the offset of where that
			// string is used within
			function_name = get_func_off_str(ea);

			// Get the string contents of an effective address. `ea` represents the
			// linear address, `len` of -1 indicates the intent to calculate the max
			// string length, and `type` of STRTYPE_C determines how the string will
			// be parsed. Failure gets empty string
			string_name = get_strlit_contents(ea, -1, STRTYPE_C);

			// Get the first data xref to `ea`. This function is quite a bit more
			// complex than some of its peers so check out the formal documentation:
			// https://www.hex-rays.com/products/ida/support/idadoc/313.shtml
			xref_first = get_first_dref_to(ea);
			
			// Get the second data xref to `ea`. Refer to the link above for more
			// detailed information on how exactly these two functions work
			xref_second = get_next_dref_to(ea, get_first_dref_to(ea));
      
			if(xref_second == BADADDR && xref_first != BADADDR)
			{
				ida_bundle.add(BundleItem(string_name, function_name, 0, xref_first));		
			}
		}
	}
	return ida_bundle;
}

/*
 * Get Bundle Item
 *
 * Parse a line of the `bundle.json` and populate a `BundleItem`.
 *
 * Traversing the `bundle.json` on a line by line basis utilizing hardcoded
 * indicies is not the most elegant solution but for the purposes of this
 * program, it works. Part of the original requirements were to build a
 * fully fledged JSON parser, however time constaints forced the retirement
 * from that commitment.
 */
static get_bundle_item(line)
{
	auto middle_position, eof_val, function_name, string_name;
	
	// Search a substring in a string
	middle_position = strstr(line, "\": \"");
	eof_val = strstr(line, ",");
	
	if(eof_val != -1)
	{
		function_name = line[middle_position + 4 : strlen(line) - 3];
	}	
	else
	{
		function_name = line[middle_position + 4 : strlen(line) - 2];
	}
	string_name = line[5 : middle_position];
	
	return BundleItem(string_name, function_name, 0, 0);
}

/*
 * Read JSON Bundle
 *
 * Reads the `bundle.json` file line by line.
 *
 * For every line parsed, until the end of the file, the content is added to
 * an instance of the `List` class via a `BundleItem`.
 */
static read_json_bundle(filename) 
{
	auto fp, line;
	auto json_bundle = List();
	
	fp = fopen(filename, "r");
	do {

		// Returns a string from a file handle. EOF can be checked via calling
		// !value_is_string(retvalue). Thread-safe function
		line = readstr(fp);
		if (line != -1)
		{
			json_bundle.add(get_bundle_item(line));
		}
	} while (line != -1);
	
	return json_bundle;
}

/*
 * Rename Functions
 *
 * Relabel functions by linear address if the strings from the bundle match.
 *
 * Iterate both the IDA bundle and the JSON bundle to search for strings that
 * match exactly. In the event that they do, get the function address from the
 * IDA-DB and appropriately rename the function.
 */
static rename_functions(ida_bundle, json_bundle)
{
	auto i, j, function_name, function_address;

	for (i = 0; i < ida_bundle.size(); i++)
	{
		for (j = 0; j < json_bundle.size(); j++)
		{
			if (ida_bundle[i].string_from_bundle == json_bundle[j].string_from_bundle)
			{
				function_name = get_func_name(ida_bundle[i].str_xref_from_ida);

				// Get the linear address of a name. BADADDR if no name
				function_address = get_name_ea_simple(function_name);

				// Rename an address
				MakeName(function_address, json_bundle[j].func_from_bundle);
			}
		}
	}
}

/*
 * Main
 *
 * Program flow manager and console interactions.
 *
 * Exists largely by requirement and in small part as a high level program
 * manager. Good for debugging as well.
 */
static main() 
{
	auto json_bundle, ida_bundle,i; 
	
	Message("Attempting to generate IDA bundle ...\n");
	
	ida_bundle = get_ida_bundle();
	
	Message("IDA bundle generated ...\n");
	
	Message("Attempting to read JSON file...\n");
	json_bundle = read_json_bundle(AskFile(0, "json_bundle.json", "Select the json bundle"));
	
	Message("JSON file processed and JSON bundle created...\n");
	
	Message("Attempting to rename functions...\n");
	rename_functions(ida_bundle, json_bundle);
	
	Message("Rename Completed\n");
}
