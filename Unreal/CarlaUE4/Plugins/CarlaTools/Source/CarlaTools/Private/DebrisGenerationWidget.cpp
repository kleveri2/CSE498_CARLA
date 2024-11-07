// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.


#include "DebrisGenerationWidget.h"
#include "Engine/Engine.h"

#define DEBUG_MSG(x, ...) if(GEngine){GEngine->AddOnScreenDebugMessage(-1, 15.0f, FColor::Red, FString::Printf(TEXT(x), __VA_ARGS__));}

UDebrisGenerationWidget::UDebrisGenerationWidget()
{
}

UDebrisGenerationWidget::~UDebrisGenerationWidget()
{
}

void UDebrisGenerationWidget::Hello()
{
	DEBUG_MSG("Hello")
}

void UDebrisGenerationWidget::GenerateDebris()
{
	DEBUG_MSG("Generate Debris")
}

void UDebrisGenerationWidget::ClearDebris()
{
	DEBUG_MSG("Clear Debris")
}

UWorld* UDebrisGenerationWidget::MyGetWorld() {
    // https://stackoverflow.com/questions/58582638/get-game-state-inside-editor-widget-in-unreal-engine-4
    // Prefer PIE Worlds.
    // Fallback to Game Preview Worlds.
    // Ignore all other types (e.g., other preview worlds).

    UWorld* PIE = nullptr;
    UWorld* GamePreview = nullptr;

    for (FWorldContext const& Context : GEngine->GetWorldContexts())
    {
        switch (Context.WorldType)
        {
        case EWorldType::PIE:
            PIE = Context.World();
            break;
        case EWorldType::GamePreview:
            GamePreview = Context.World();
            break;
        }
    }

    if (PIE)
    {
        DEBUG_MSG("PIE")
        return PIE;
    }
    else if (GamePreview)
    {
        DEBUG_MSG("GamePreview")
        return GamePreview;
    }
    DEBUG_MSG("No world")
    return nullptr;
}

void UDebrisGenerationWidget::OverWriteMesh(UStaticMesh* Mesh, UStaticMesh* NewMesh)
{
    // From: https://forums.unrealengine.com/t/is-it-possible-to-render-mesh-passed-to-niagara/648742/10
    FMeshDescription& Okay = *NewMesh->GetMeshDescription(0);
    const FStaticMeshLODResources& Lod = NewMesh->GetLODForExport(0);

    TArray<const FMeshDescription*> MeshDescriptionPtrs;
    MeshDescriptionPtrs.Emplace(&Okay);
    Mesh->BuildFromMeshDescriptions(MeshDescriptionPtrs);
}

void UDebrisGenerationWidget::Weather(float choice)
{
    FString Python = TEXT("python");
    FString Script;

    FString Dir = FPaths::ProjectDir();

    Dir = Dir.Replace(TEXT("/Unreal/CarlaUE4"), TEXT("")); 

    if (choice == 0)
    {
        Script = FPaths::Combine(Dir, TEXT("PythonAPI"), TEXT("examples"), TEXT("rain.py"));
    }
    else if (choice == 1)
    {
        Script = FPaths::Combine(Dir, TEXT("PythonAPI"), TEXT("examples"), TEXT("wind.py"));
    }
    else if (choice == 2)
    {
        Script = FPaths::Combine(Dir, TEXT("PythonAPI"), TEXT("examples"), TEXT("wind-rain.py"));
    }
    else if (choice == 3)
    {
        Script = FPaths::Combine(Dir, TEXT("PythonAPI"), TEXT("examples"), TEXT("dark-rain.py"));
    }
    else if (choice == 4)
    {
        Script = FPaths::Combine(Dir, TEXT("PythonAPI"), TEXT("examples"), TEXT("dynamic_weather.py"));
    }
    else if (choice == 5)
    {
        Script = FPaths::Combine(Dir, TEXT("PythonAPI"), TEXT("examples"), TEXT("sun.py"));
    }
    else if (choice == 6)
    {
        Script = FPaths::Combine(Dir, TEXT("PythonAPI"), TEXT("examples"), TEXT("fog.py"));
    }

    Script = FPaths::ConvertRelativePathToFull(Script);

    FString Params = FString::Printf(TEXT("\"%s\""), *Script);

    FString Folder = FPaths::Combine(Dir, TEXT("PythonAPI"), TEXT("examples"));

    // Launch the process
    FProcHandle ProcHandle = FPlatformProcess::CreateProc(*Python, *Params, true, false, false, nullptr, 0, *Folder, nullptr);
    if (ProcHandle.IsValid())
    {
        DEBUG_MSG("It Worked :-)");
    }
    else
    {
        DEBUG_MSG("Failed :-(");
    }
}

